import boto3
import time

MAX_TRY = 20

def update_service(client, cluster, service, desired_count, sleep_time=180):
    client.update_service(cluster=cluster,
                          service=service,
                          desiredCount=desired_count)
    
    if desired_count > 1:
        # wait until all running
        print(f'모두 RUNNING이 되도록 {sleep_time}초 동안 기다릴게요!')
        time.sleep(sleep_time)

def keep_only_n_task(client, cluster, service, n):
    response = client.list_tasks(cluster=cluster,
                                serviceName=service,
                                desiredStatus='RUNNING')
    for _ in range(n):
        response['taskArns'].pop()
    
    for task_arn in response['taskArns']:
        client.stop_task(cluster=cluster,
                         task=task_arn)

    response = client.list_tasks(cluster=cluster,
                                serviceName=service,
                                desiredStatus='RUNNING')
    assert len(response['taskArns']) == n, f"{len(response['taskArns'])}개의 task가 남았어요."

def check_task_status(client, cluster, service, sleep_time=30):
    response = client.list_tasks(cluster=cluster,
                                serviceName=service)
    tasks = response['taskArns']
    
    for _ in range(MAX_TRY):
        # RUNNING으로 status에 filter를 걸어도 PEDDDING, ACTIVATING이 모두 잡혀버림
        response = client.describe_tasks(cluster=cluster, tasks=tasks)
        for task in response['tasks']:
            if task['lastStatus'] != 'RUNNING':
                print(f'RUNNING 상태가 아닌 task가 있어서 {sleep_time}초 동안 기다릴게요!')
                time.sleep(sleep_time)
    
    response = client.describe_tasks(cluster=cluster, tasks=tasks)
    for task in response['tasks']:
        assert task['lastStatus'] == 'RUNNING', f'{MAX_TRY}번 시도후에도 모든 task가 RUNNING 상태가 아니예요.'
