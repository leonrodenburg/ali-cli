# Ali CLI

Wraps the Alibaba Cloud SDK to make complicated tasks a lot simpler.

To make this work, you will either need to use the official Aliyun CLI to configure your credentials (run `aliyun configure`) or
create the file `~/.aliyun/config.json` with the following contents:

```json
{
  "current": "default",
  "profiles": [
    {
      "name": "default",
      "mode": "AK",
      "access_key_id": "<ACCESS_KEY_ID>",
      "access_key_secret": "<ACCESS_KEY_SECRET>",
      "sts_token": "",
      "ram_role_name": "",
      "ram_role_arn": "",
      "ram_session_name": "",
      "private_key": "",
      "key_pair_name": "",
      "expired_seconds": 0,
      "verified": "",
      "region_id": "eu-central-1",
      "output_format": "json",
      "language": "zh",
      "site": "",
      "retry_timeout": 0,
      "retry_count": 0
    }
  ]
}
```

Replace `<ACCESS_KEY_ID>` with your access key ID and `<ACCESS_KEY_SECRET>` with your access key secret. Optionally, you can change the region
to the region you like (`eu-central-1` is Frankfurt).
