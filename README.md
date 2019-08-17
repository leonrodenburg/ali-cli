# Ali CLI

[![PyPI version](https://img.shields.io/pypi/v/ali-cli.svg?colorB=brightgreen)](https://pypi.org/project/ali-cli/)
[![Build status](https://img.shields.io/circleci/project/github/leonrodenburg/ali-cli/master.svg)](https://circleci.com/gh/leonrodenburg/ali-cli)
[![Code coverage](https://img.shields.io/codecov/c/github/leonrodenburg/ali-cli.svg)](https://codecov.io/gh/leonrodenburg/ali-cli)

Wraps the Alibaba Cloud SDK to make complicated tasks a lot simpler.

## Installation

Installation is easy, run the following command to install the CLI through Pip:

```bash
pip install ali-cli
```

Then run the CLI using the command `ali`. You should see the default help output with the supported commands.

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
      "access_key_id": "ACCESS_KEY_ID",
      "access_key_secret": "ACCESS_KEY_SECRET",
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

Replace `ACCESS_KEY_ID` with your access key ID and `ACCESS_KEY_SECRET` with your access key secret. Optionally, you can change the region to the region you like (`eu-central-1` is Frankfurt).

## Supported services

- [Key Management Service (KMS)](#kms) - [documentation](https://www.alibabacloud.com/help/product/28933.htm?spm=a2c63.m28257.a1.91.3c9d5922IB2dod)
- [Message Service (MNS)](#mns) - [documentation](https://www.alibabacloud.com/help/product/27412.htm?spm=a3c0i.7961101.1204782.1.2acc580293hZ9R)
- [Resource Orchestration Service (ROS)](#ros) - [documentation](https://www.alibabacloud.com/help/product/28850.htm?spm=a2796.128466.1198106.1.73aa2f6aqdY9Nh)

## Other features

- [Client-side cryptography with OSS](#crypto) - [OSS documentation](https://www.alibabacloud.com/help/product/31815.htm?spm=a3c0i.7950270.1167928.3.5761ab91pLZinG)

### <a name="kms"></a> Key Management Service (KMS)

Supports listing of Customer Master Keys (CMK), encryption and decryption with and without data key.

To see a list of supported commands, use `ali kms`.

### <a name="mns"></a> Message Service (MNS)

As the official Alibaba Cloud CLI has no support for Message Service, we decided that it would be nice to have support for it in Ali CLI. We currently support the following operations on queues and messages:

- Creating a queue - `ali mns queue create --name NAME`
- Listing queues - `ali mns queue list`
- Getting queue attributes - `ali mns queue get --name NAME`
- Deleting a queue - `ali mns queue delete --name NAME`

- Sending a message - `echo '{"success": true}' | ali mns queue send-message --name NAME --message-body -`
- Receiving a single message - `ali mns queue receive-message --name NAME`
- Receiving a batch of messages - `ali mns queue receive-messages --name NAME --num-of-messages 10`
- Peeking at a message - `ali mns queue peek-message --name NAME`
- Peeking at a batch of messages - `ali mns queue peek-messages --name NAME --num-of-messages 10`
- Deleting a message from a queue - `ali mns queue delete-message --name NAME --handle RECEIPT_HANDLE`

Topics and subscriptions will be supported at a later point in time.

### <a name="ros"></a> Resource Orchestration Service (ROS)

Ali CLI supports most of the ROS functions. This allows you to deploy JSON templates as stacks,
so you can use code to define your whole infrastructure.

To deploy an example bucket, run the following command:

```bash
ali ros create-stack --name ali-ros-test --template examples/ros/bucket.json --parameters BucketName=my-fancy-bucket
```

This will create the stack `ali-ros-test`, using the template in the `examples/ros/bucket.json` file and specifies the values to use for the
template parameters. You can specify multiple parameters if necessary by repeating the `--parameters <key>=<val>` option as many times as you need.
Feel free to modify the stack name and templates if you like. You can also specify `-` for the template, which means that it
will be read from stdin. Type or paste the template in the prompt and press Ctrl-D to send it into the CLI.

To list stacks, run `ali ros describe-stacks`. This will output all the stacks in the current region.

To delete a stack, run `ali ros delete-stack --name ali-ros-test`. This will remove the stack you created above, including the provisioned resources.

Although the Alibaba ROS API's only support JSON templates, Ali CLI can also deploy YAML templates. We do this by converting your YAML into JSON
before creating the stack. Examples of both JSON and YAML templates can be found in the `examples/ros` directory.

### <a name="crypto"></a> Client-side cryptography with OSS

When you store your data in the cloud, it sometimes feels a bit weird to use services like KMS. With KMS, the keys that are used for encryption are
generated by the cloud provider, and you have to trust them not to misuse the keys to decrypt your data. If you cannot or don't want to trust your
provider, client-side encryption is the way to go. Ali CLI has some basic features for automating client-side encryption, so you don't have to do it
yourself. The following features are suppored:

- Generating a secret key - `ali crypto generate-key -k KEYFILE`
- Encrypting data with a secret key - `ali crypto encrypt -k KEYFILE -s STRING`
- Decrypting data with a secret key - `ali crypto decrypt -k KEYFILE -s STRING`

- Upload file or directory to OSS with encryption - `ali crypto oss cp LOCAL_PATH oss://BUCKET/PATH -k KEYFILE`
- Download encrypted files from OSS and decrypt - `ali crypto oss cp oss://BUCKET/PATH LOCAL_PATH -k KEYFILE`
