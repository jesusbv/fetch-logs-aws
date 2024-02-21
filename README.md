# fetch-logs-aws

To fetch all AWS instances logs change or set `instances_name`
to the `Name` value used when creating the instances and run it like

```bash
bash scp_all_instances_logs.py
```
or
```bash
python3 scp_all_instances_logs.py
```

The script fetches the specified logs from all the instances
and deletes the instances

The script creates a directory `ip_logs_<number_of_instances>`
where it creates a directory per instance with its IP address
and saves every instance log inside that directory

When script has finished, the expection is that said instances are deleted


## NOTES

This script uses aws credentials, it is expected that said credentials are configured
on the system running the script
