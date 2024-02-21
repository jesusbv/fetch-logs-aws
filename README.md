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

When script has finished, the expection is that said instances are deleted
