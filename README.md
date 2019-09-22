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
- [Message Notification Service (MNS)](#mns) - [documentation](https://www.alibabacloud.com/help/product/27412.htm?spm=a3c0i.7961101.1204782.1.2acc580293hZ9R)
- [Resource Orchestration Service (ROS)](#ros) - [documentation](https://www.alibabacloud.com/help/product/28850.htm?spm=a2796.128466.1198106.1.73aa2f6aqdY9Nh)

## Supported workflows

- [Client-side cryptography with Object Storage Service (OSS)](#crypto) - [documentation](https://www.alibabacloud.com/help/product/31815.htm?spm=a3c0i.7950270.1167928.3.5761ab91pLZinG)

## <a name="kms"></a> Key Management Service (KMS)

Supports listing of Customer Master Keys (CMK), encryption and decryption with and without data key.

To see a list of supported commands, use `ali kms`.

## <a name="mns"></a> Message Notification Service (MNS)

As the official Alibaba Cloud CLI has no support for Message Notification Service, we decided that it would be nice to have support for it in Ali CLI. We currently
support the following operations on queues and messages.

### Queue operations

Creating a queue - `ali mns queue create --name NAME`<br>
Listing queues - `ali mns queue list`<br>
Getting queue attributes - `ali mns queue get --name NAME`<br>
Deleting a queue - `ali mns queue delete --name NAME`<br>

### Message operations

Sending a message - `echo '{"success": true}' | ali mns queue send-message --name NAME --message-body -`<br>
Receiving a single message - `ali mns queue receive-message --name NAME`<br>
Receiving a batch of messages - `ali mns queue receive-messages --name NAME --num-of-messages 10`<br>
Peeking at a message - `ali mns queue peek-message --name NAME`<br>
Peeking at a batch of messages - `ali mns queue peek-messages --name NAME --num-of-messages 10`<br>
Deleting a message from a queue - `ali mns queue delete-message --name NAME --handle RECEIPT_HANDLE`

Topics and subscriptions will be supported at a later point in time.

## <a name="ros"></a> Resource Orchestration Service (ROS)

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

## <a name="crypto"></a> Client-side cryptography with Object Storage Service (OSS)

When you store your data in the cloud, it sometimes feels a bit weird to use services like Key Management Service (KMS). With KMS, the keys that are used
for encryption are generated by the cloud provider, and you have to trust them to not misuse the keys and decrypt your data. If you cannot or do not want
to trust your provider, client-side encryption can be a solution for your most valuable data. Ali CLI has some basic features for automating client-side
encryption, so you don't have to do it yourself. The following features are supported:

### Prequisite: Generating a key

To encrypt or decrypt data, we first need a key:

`ali crypto generate-key -k KEYFILE`

The generated secret key will be put in the `KEYFILE` path. This file is extremely important and should be kept somewhere safe. If the key file is lost,
you will lose access to all the data that has been encrypted with the key. There is no way to resolve this.

The encryption mechanism uses a [Fernet symmetric key](https://cryptography.io/en/latest/fernet/) for encryption and decryption. The key's contents are
written to `KEYFILE` directly. This means that anyone with access to that file is also able to decrypt your data. Be careful with handing out the keyfile
to others. Keep a copy of the key offline in a safe (on a USB stick or write the key out on paper) and remove the key from your computer as soon as you
are done with it. For convenience, you could decide to store a copy of the key online. I would suggest you to store the key separated from the data,
preferrably in the online storage solution of a different cloud provider. Be sure to enable encryption on the bucket.

### Encrypting / decrypting locally

The keyfile can be used to encrypt / decrypt strings and files locally. Here are a few examples:

```sh
ali crypto encrypt -k KEYFILE -s PLAIN_TEXT # Encrypt string
ali crypto decrypt -k KEYFILE -s ENCRYPTED_STRING # Decrypt string

ali crypto encrypt -k KEYFILE -f FILE_TO_ENCRYPT # Encrypt file at path
ali crypto decrypt -k KEYFILE -f FILE_TO_DECRYPT # Decrypt file at path
```

As an example, let's say you want to encrypt your very secure password `MyPassword1234`. To do this, follow these steps:

```sh
[leon@home ~] ali crypto generate-key -k my-key
> Successfully created secret key in my-key
[leon@home ~] ali crypto encrypt -k my-key -s MyPassword1234
> gAAAAABdhyODhPOc9UdcRQ1lTXOTZC2q-bsuhcQqhfoG4Jf... # trimmed for readability
[leon@home ~] ali crypto decrypt -k my-key -s gAAAAABdhyODhPOc9UdcRQ1lTXOTZC2q-bsuhcQqhfoG4Jf...
> MyPassword1234
```

File encryption only supports files, not directories.

### Automatic upload / download of encrypted files to OSS

To solve the problems outlined in the introduction of this workflow, it can be very handy to employ client-side encryption when uploading sensitive
files to a cloud provider's storage solution. Using Ali CLI, you can conveniently upload files and directories to a bucket, automatically encrypting
them with a keyfile on your computer. When you download them again, the files will be downloaded and decrypted locally again. Only encrypted data
will be transferred over the wire and stored in the OSS bucket.

The CLI commands are very simple and largely mirror the commands of the official CLI:

```sh
# Copy from local directory / file to bucket
ali crypto oss cp LOCAL_PATH oss://BUCKET/PATH -k KEYFILE

# Copy from bucket to local file / directory
ali crypto oss cp oss://BUCKET/PATH LOCAL_PATH -k KEYFILE
```

As the files are encrypted and decrypted locally, the keyfile is very important. If you lose it, the online data also becomes useless.
