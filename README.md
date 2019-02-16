# Ali CLI

Wraps the Alibaba Cloud SDK to make complicated tasks a lot simpler.

## Installation

There is no PyPI package yet, so you need to use [Pipenv](https://github.com/pypa/pipenv) to manually install the package in editable mode and run it:

```bash
pipenv install -e .
pipenv shell
ali
```

You should see the default help output with the supported commands.

## Configuration

To connect the CLI to your Alibaba Cloud account, you will either need to use the official [Aliyun CLI](https://github.com/aliyun/aliyun-cli) to
configure your credentials or create the configuration manually. To use the CLI, run `aliyun configure` and follow the prompts. If you don't want
to install the official CLI, you can manually create the file `~/.aliyun/config.json` with the following contents:

```json
{
  "current": "",
  "profiles": [
    {
      "name": "",
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

## Usage

Currently, Ali CLI only supports commands related to the Resource Orchestration Service (ROS). This allows you to deploy JSON templates as stacks,
so you can use code to define your whole infrastructure.

To deploy an example bucket, run the following command:

```bash
ali ros create-stack --name ali-ros-test --template-path examples/ros/bucket.json --parameters BucketName=my-fancy-bucket
```

This will create the stack `ali-ros-test`, using the template in the `examples/ros/bucket.json` file and specifies the values to use for the
template parameters. Feel free to modify the stack name and templates if you like.

To list stacks, run `ali ros describe-stacks`. This will output all the stacks in the current region.

To delete a stack, run `ali ros delete-stack --name ali-ros-test`. This will remove the stack you created above, including the provisioned resources.
