import boto3
import time

MAX_TRY = 20
ELB_DEFAULT_HEALTH_CHECK_SEC = 30

def check_target_group_health(client, target_group_arn, n_task):
    for _ in range(MAX_TRY):
        target_health = client.describe_target_health(TargetGroupArn=target_group_arn)
        health_desc = target_health['TargetHealthDescriptions']
        if not health_desc:
            print(f'elb target group에 아무것도 없어서 {ELB_DEFAULT_HEALTH_CHECK_SEC}초 동안 기다릴게요.')
            time.sleep(ELB_DEFAULT_HEALTH_CHECK_SEC)
        else:
            healthy_count = 0
            for target in target_health['TargetHealthDescriptions']:
                if target['TargetHealth']['State'] == 'healthy':
                    healthy_count += 1
            
            if healthy_count == n_task:
                print(f'전체 {n_task}개 모두 healthy!')
                break
            elif healthy_count > 0:
                print(f'전체 {n_task}개 중 {healthy_count}개만 healthy')
                time.sleep(ELB_DEFAULT_HEALTH_CHECK_SEC)
            else:
                print(f'healthy target 없음')
                time.sleep(ELB_DEFAULT_HEALTH_CHECK_SEC)