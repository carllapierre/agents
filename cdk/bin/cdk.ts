import * as cdk from 'aws-cdk-lib';
import { App, Stack, StackProps } from 'aws-cdk-lib';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecsPatterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as fs from 'fs';
import * as path from 'path';

interface EnvProps extends StackProps {
    envName: string;
}

class AgentStack extends Stack {
    constructor(scope: cdk.App, id: string, serviceName: string, props: EnvProps) {
        super(scope, id, props);

        const vpc = new ec2.Vpc(this, `${props.envName}-${serviceName}-Vpc`, { maxAzs: 2 });

        const cluster = new ecs.Cluster(this, `${props.envName}-${serviceName}-Cluster`, { vpc });

        const repository = new ecr.Repository(this, `${props.envName}-${serviceName}-repository`);

        const table = new dynamodb.Table(this, `${props.envName}-${serviceName}-Table`, {
            partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING }
        });

        const fargateTaskDefinition = new ecs.FargateTaskDefinition(this, `${props.envName}-${serviceName}-TaskDef`);

        const container = fargateTaskDefinition.addContainer(`${props.envName}-${serviceName}-Container`, {
            image: ecs.ContainerImage.fromAsset(path.join(__dirname, '../../repository', serviceName)),
            memoryLimitMiB: 512,
            logging: new ecs.AwsLogDriver({ streamPrefix: `${serviceName}-ecs` }),
        });

        container.addPortMappings({
            containerPort: 80,
            protocol: ecs.Protocol.TCP
        });

        new ecsPatterns.ApplicationLoadBalancedFargateService(this, `${props.envName}-${serviceName}-FargateService`, {
            cluster,
            taskDefinition: fargateTaskDefinition,
        });

        new cdk.CfnOutput(this, `${props.envName}-${serviceName}-LoadBalancerDNS`, {
            value: `${serviceName}-FargateService.loadBalancer.loadBalancerDnsName`,
        });
    }
}

const app = new cdk.App();

const servicesPath = path.join(__dirname, '../../repository');
const services = fs.readdirSync(servicesPath).filter(f => fs.lstatSync(path.join(servicesPath, f)).isDirectory());

services.forEach(serviceName => {
    new AgentStack(app, `${serviceName}-stack-dev`, serviceName, { envName: 'dev' });
    new AgentStack(app, `${serviceName}-stack-prod`, serviceName, { envName: 'prod' });
});

app.synth();
