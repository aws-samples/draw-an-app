#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ToHtmlStack } from '../lib/tohtml-stack';

const app = new cdk.App();
new ToHtmlStack(app, 'ToHtmlStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-west-2'
  }
});
