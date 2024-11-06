import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import * as path from "path";
import { DockerImageAsset, Platform } from 'aws-cdk-lib/aws-ecr-assets';

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

    // Create Fargate Service with ALB
    const fargateService = new ecs_patterns.ApplicationLoadBalancedFargateService(this, 'ToHtmlService', {
      cluster: cluster,
      cpu: 256,
      desiredCount: 1,
      taskImageOptions: {
        image: ecs.ContainerImage.fromAsset(path.join(__dirname, "../../src"), {
          platform: Platform.LINUX_AMD64,  // Necessary when deploying from ARM64 machines
      }),
        environment: {
          AWS_DEFAULT_REGION: 'us-west-2'
        },
        containerPort: 8000
      },
      memoryLimitMiB: 512,
      publicLoadBalancer: true,
      assignPublicIp: true
    });

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

    // Configure health check
    fargateService.targetGroup.configureHealthCheck({
      path: '/api/health',
      interval: cdk.Duration.seconds(120),
      timeout: cdk.Duration.seconds(30)
    });

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
