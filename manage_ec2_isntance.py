import boto3
import signal

def start_instance(instance_id):
    ec2 = boto3.client('ec2')
    ec2.start_instances(InstanceIds=[instance_id])
    print(f"Starting instance {instance_id}")

def stop_instance(instance_id):
    ec2 = boto3.client('ec2')
    ec2.stop_instances(InstanceIds=[instance_id])
    print(f"Stopping instance {instance_id}")

def list_all_instances():
    ec2 = boto3.client('ec2')
    # Retrieve all instances
    instances = ec2.describe_instances()['Reservations']

    # Loop through the instances
    for instance in instances:
        for i in instance['Instances']:
            if 'Tags' in i:
                instance_name = None
                for tag in i['Tags']:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                        break
                if instance_name:
                    print(instance_name)
                else:
                    print(i['InstanceId'])
            else:
                print(i['InstanceId'])


def get_instance_name(instance):
    name = None
    tags = instance.get('Tags', [])
    for tag in tags:
        if tag.get('Key') == 'Name':
            name = tag.get('Value')
    return name or instance.get('InstanceId')

def get_instances(state):
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [state]
            }
        ]
    )
    return [
        {
            'InstanceId': instance['InstanceId'],
            'Name': get_instance_name(instance)
        }
        for reservation in instances['Reservations']
        for instance in reservation['Instances']
    ]

def list_instances(instances):
    instance_count = 0
    for i, instance in enumerate(instances):
        print(f"{i+1}. {instance['Name']}")
        instance_count = i
    print(f"{instance_count+2}. Cancel")

def select_instance(instances):
    while True:
        list_instances(instances)
        selection = input("Select an instance: ")
        try:
            index = int(selection) - 1
            if 0 <= index < len(instances):
                return instances[index]['InstanceId']
            elif index == len(instances):
                print()
                main_menu()
        except ValueError:
            pass
        print()
        print("Invalid selection!")
        print()
        print("Select a valid instance:")

def main_menu():
    signal.signal(signal.SIGINT, handler)
    print("1. Start instance")
    print("2. Stop instance")
    print("3. List instances")
    print("4. Quit")
    print()
    while True:
        selection = input("Enter a number: ")
        if selection == '1':
            instances = get_instances('stopped')
            if not instances:
                print("No stopped instances")
                print()
                main_menu()
            instance_id = select_instance(instances)
            start_instance(instance_id)
            print()
            action_menu()
        elif selection == '2':
            instances = get_instances('running')
            if not instances:
                print("No running instances")
                print()
                main_menu()
            instance_id = select_instance(instances)
            stop_instance(instance_id)
            action_menu()
        elif selection == '3':
            print()
            print("All instances:")
            list_all_instances()
            print()
            main_menu()
        elif selection == '4':
            print()
            print("Exiting...")
            quit()
        else:
            print("Invalid selection")
            print()

 

def action_menu():
    print("1. Start/Stop another instance")
    print("2. Go back to main menu")
    print("3. Quit")
    print()
    while True:
        selection = input("Enter a number: ")
        if selection == '1':
            print()
            main_menu()
        elif selection == '2':
            print()
            main_menu()
        elif selection == '3':
            print("Exiting...!")
            quit()
        else:
            print("Invalid selection")
            print()

def handler(signum, frame):
        print()
        print("Closing Application...")
        print()
        exit(1)

main_menu()