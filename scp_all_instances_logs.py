#!/bin/python3

import datetime
import json
import os
import subprocess

"""
Change <Name> for the name you are searching

You can use AWS filter + query combination to get the info:

> aws ec2 describe-instances \
--filters Name=tag:Name,Values='<Name>' Name=instance-state-name,Values=running \
--query "Reservations[*].Instances[*][].{Instance:InstanceId,Network:PublicIpAddress}" \
--region eu-central-1
[
 {
        "Instance": "i-054bd54108048d214",
        "Network": "35.159.16.140"
    },
    {
        "Instance": "i-0d1bf0d0d90cfeff4",
        "Network": "54.93.120.81"
    },
    {
        "Instance": "i-045d6a677db073ed0",
        "Network": "35.156.114.242"
    }
]

for reference:
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_Filtering.html
https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-filter.html#cli-usage-filter-client-side

or you can use jq:

> aws ec2 describe-instances
--filters Name=tag:Name,Values='<Name>' Name=instance-state-name,Values=running
--region eu-central-1 | jq '.Reservations[].Instances[] | .PublicIpAddress + " " + .InstanceId'
"35.159.16.140 i-054bd54108048d214"
"54.93.120.81 i-0d1bf0d0d90cfeff4"
"35.156.114.242 i-045d6a677db073ed0"
"""


def get_instances_info(instances_name: str) -> list:
    """Get the instance id and public ip addresses.

    Get the info From all the running instances with name instances_name
    """
    aws_cmd = (
        'aws ec2 describe-instances '
        f"--filters Name=tag:Name,Values={instances_name} "
        "Name=instance-state-name,Values=running "
        '--query Reservations[*].Instances[*][].'
        '{Instance:InstanceId,PublicIpAddress:PublicIpAddress} '
        '--region eu-central-1 --output json'
    )

    all_instances_info = subprocess.Popen(
        aws_cmd.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, error = all_instances_info.communicate()
    return json.loads(output.decode())


def creates_directory_to_download_log(n_instances: int) -> str:
    """Create directory and return directory name."""
    # DONE: rename with better name and add number of instances dynamically
    logs_directory = f"ips_logs_{str(n_instances)}"
    try:
        os.makedirs(logs_directory, exist_ok=False)
    except OSError:
        now_time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        now_time = '_'.join([now_time])
        logs_directory = '_'.join([logs_directory, now_time])
        os.makedirs(logs_directory)

    return logs_directory


def delete_instances(instances_info: list) -> None:
    """Delete all the instances with ids in iids."""
    # FROM THE DOCS
    # Constraints: Up to 1000 instance IDs.
    # We recommend breaking up this request into smaller batches.
    # https://docs.aws.amazon.com/cli/latest/reference/ec2/terminate-instances.html
    iids = [info['Instance'] for info in instances_info if info['Instance']]
    aws_delete_instances_cmd = (
        f"aws ec2 terminate-instances --instance-id {' '.join(iids)} "
        '--region eu-central-1'
    )
    print(aws_delete_instances_cmd)
    instances_deleted_info = subprocess.Popen(
        aws_delete_instances_cmd.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, error = instances_deleted_info.communicate()
    print(output.decode())


def fetch_log(instances_info: list, logs_directory: str) -> None:
    """Fetch the log file from all the instances in instances_info."""
    errors = 0
    for info in instances_info:
        download_log_cmd = (
            'scp -i ~/.ssh/jesus-eu-central-1.pem -o StrictHostKeyChecking=no '
            f"ec2-user@{info['PublicIpAddress']}:"
            '/home/ec2-user/zypper_timeout '
            f"{logs_directory}/{info['PublicIpAddress']}"
        )
        print(download_log_cmd)
        p = subprocess.Popen(download_log_cmd.split())
        output, error = p.communicate()
        if p.returncode:
            # FROM THE DOCS
            # Constraints: Up to 1000 instance IDs.
            # We recommend breaking up this request into smaller batches.
            # https://docs.aws.amazon.com/cli/latest/reference/ec2/terminate-instances.html
            print(
                f"There was an error scopying from instance {info['Instance']}"
            )
            errors = errors + 1
            info['Instance'] = False

    print(f"There was {errors} processing the instances")


# TODO: get instances Name filter from args
# TODO: get the directory for logs  from args
instances_name = '<filter_name>'
instances_info = get_instances_info(instances_name)
logs_directory = creates_directory_to_download_log(len(instances_info))
fetch_log(instances_info, logs_directory)
# iids = [info['Instance'] for info in instances_info if info['Instance']]
delete_instances(instances_info)

print(
    f"Info from all the instances has been scp copied to {logs_directory} "
    'and instances have been deleted'
)
