import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import * as path from "path";
import { DockerImageAsset, Platform } from 'aws-cdk-lib/aws-ecr-assets';
import * as elasticloadbalancingv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';

export class ToHtmlStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create VPC
    const vpc = new ec2.Vpc(this, 'ToHtmlVpc', {
      maxAzs: 2
    });

    // Create ECS Cluster
    const cluster = new ecs.Cluster(this, 'ToHtmlCluster', {
      vpc: vpc
    });


    // Create Fargate Service with Multiple Target Groups
    const fargateService = new ecs_patterns.ApplicationMultipleTargetGroupsFargateService(this, 'ToHtmlService', {
      cluster,
      cpu: 256,
      desiredCount: 1,
      memoryLimitMiB: 512,
      taskImageOptions: {
        image: ecs.ContainerImage.fromAsset(path.join(__dirname, "../../src"), {
          platform: Platform.LINUX_AMD64,  // Necessary when deploying from ARM64 machines
        }),
        environment: {
          AWS_DEFAULT_REGION: 'us-west-2'
        },
        containerName: 'tohtml-container'
      },
      loadBalancers: [{
        name: 'ToHtmlLB',
        publicLoadBalancer: true,
        listeners: [
                        {
                            protocol: elasticloadbalancingv2.ApplicationProtocol.HTTP,                            
                            name: 'fg-alb-http'
                        }
                    ]                
      }],
      targetGroups: [        
        {
          containerPort: 3000,
          listener: 'fg-alb-http',          
        },
        {
          containerPort: 8000,
          listener: 'fg-alb-http',
          pathPattern: '/api/*',
          priority: 2,
          // healthCheck: {
          //   path: '/ui/',
          //   interval: cdk.Duration.seconds(120),
          //   timeout: cdk.Duration.seconds(30)
          // }
        }
      ]
    });

     fargateService.targetGroup.configureHealthCheck({
            path: '/api/health',
            healthyThresholdCount: 2,
            unhealthyThresholdCount: 5,
            interval: cdk.Duration.seconds(120),
            timeout: cdk.Duration.seconds(30)
        });

     // fargateService.targetGroup.configureHealthCheck({
     //        path: '/ui',
     //        healthyThresholdCount: 2,
     //        unhealthyThresholdCount: 5,
     //        interval: cdk.Duration.seconds(120),
     //        timeout: cdk.Duration.seconds(30)
     //    });


    // Add Bedrock permissions to the task role
    fargateService.taskDefinition.taskRole.addToPrincipalPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'bedrock:InvokeModel',          
          'bedrock:InvokeModelWithResponseStream'
        ],
        resources: ['*']  // You might want to restrict this to specific model ARNs
      })
    );

    // Configure Auto Scaling
    const scaling = fargateService.service.autoScaleTaskCount({
      maxCapacity: 4,
      minCapacity: 1
    });

    scaling.scaleOnCpuUtilization('CpuScaling', {
      targetUtilizationPercent: 70
    });

    // Output the ALB DNS name
    new cdk.CfnOutput(this, 'LoadBalancerDNS', {
      value: fargateService.loadBalancer.loadBalancerDnsName
    });
  }
}
