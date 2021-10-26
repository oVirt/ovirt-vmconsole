# OVIRT-VMCONSOLE
[![Copr build status](https://copr.fedorainfracloud.org/coprs/ovirt/ovirt-master-snapshot/package/ovirt-vmconsole/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/ovirt/ovirt-master-snapshot/package/ovirt-vmconsole/)

## OUTLINE

ovirt-vmconsole enables secure access to virtual machine serial console. It
uses SSH protocol to tunnel the console from customer to destination host.

Two components are available:

### `ovirt-vmconsole-host`

ssh daemon implementation that runs on the host end enables trusted
connections to access the consoles. Consoles are assumed to be unix domain
sockets that are directly attached to qemu virtual serial.

### `ovirt-vmconsole-proxy`

ssh daemon implementation that runs on the end user accessible host, users
access the proxy, based on their public key the authorized consoles are
fetch from a manager, once selected a connection to the host is
established.

The ovirt-vmconsole package cannot be used as-is, it requires customization
to fetch users' authorized keys and users' authorized consoles.

## SERVICES

- `ovirt-vmconsole-host-sshd`
- `ovirt-vmconsole-proxy-sshd`

## USAGE

Access to proxy by user is perform using the following command, a menu with
the available consoles will be presented:

```console
$ ssh -t -p 2222 ovirt-vmconsole@proxy-host connect
```

Access to specify console can be done using the following command:

```console
$ ssh -t -p 2222 ovirt-vmconsole@proxy-host connect --vm-id=1E12DF323
```

List available consoles:

```console
$ ssh -p 2222 ovirt-vmconsole@proxy-host list
```

Usage:

```console
$ ssh -p 2222 ovirt-vmconsole@proxy-host -- --help
```

## IMPLEMENTATION

ssh daemon implementation is based on system provided openssh, daemon is
running under non privileged user. No root access is used.

## INSTALLATION

### PKI ARTIFACTS

PKI artifacts are located at:

`/etc/pki/ovirt-vmconsole`

| Mode | Owner           | File                        | Notes                           |
| ---- | --------------- | --------------------------- | ------------------------------- |
| 0644 | root            | ca.pub                      |                                 |
| 0600 | ovirt-vmconsole | host-ssh_host_rsa           |                                 |
| 0644 | root            | host-ssh_host_rsa-cert.pub  | principal:fqdn                  |
| 0600 | ovirt-vmconsole | proxy-ssh_host_rsa          |                                 |
| 0644 | root            | proxy-ssh_host_rsa-cert.pub | principal:fqdn                  |
| 0600 | ovirt-vmconsole | proxy-ssh_user_rsa          |                                 |
| 0644 | root            | proxy-ssh_user_rsa-cert.pub | principal:ovirt-vmconsole-proxy |

### CONSOLES

By default consoles' usocks are assumed to be at:

`/var/run/ovirt-vmconsole-console/`

### CONFIGURATION

Configuration is located at the following directory, Conf.d structure,
sorted by file name, last wins.

`/etc/ovirt-vmconsole/ovirt-vmconsole-{host,proxy}/conf.d`

Packages should at least modify the following proxy configuration, refer
to `README.API`:
 - `key_list` - get a list of authorized keys.
 - `console_list` - get a list of authorized consoles.

## PROBLEM DETERMINATION

### LOGS

Logs are sent to system log, if you enable debug make sure syslog daemon
writes log records.

Enable log for specific user session can be done using:

```console
$ ssh -t -p 2222 ovirt-vmconsole@proxy-host -- --debug connect
```

### TEST

Create a socket s1 to emulate qemu, Ctrl-A to escape.

```console
socat -,raw,echo=0,escape=1 UNIX-LISTEN:/var/run/ovirt-vmconsole-console/s1,user=ovirt-vmconsole
```

## CUSTOMIZATION

It could be needed to change the TCP port the serial-console infrastructure uses
to connect to emulated serial ports.
This can be done manually, but it is not recommended way since it may easily broken by updates.

1. Override on each virtualization host the default sshd options
   using the OPTIONS variable at:

    `/etc/sysconfig/ovirt-vmconsole-host-sshd`

2. On the proxy host, edit

    `/etc/sysconfig/ovirt-vmconsole-proxy-sshd`

   You can create the file mentioned here and in the above bullet point if missing; check
   https://www.freedesktop.org/software/systemd/man/systemd.exec.html for further details.

3. On the proxy host, also override the ssh options by dropping a new file in
   the `/etc/ovirt-vmconsole/ovirt-vmconsole-proxy/conf.d/` directory, like

   `/etc/ovirt-vmconsole/ovirt-vmconsole-proxy/conf.d/90-custom-options.conf`

Use this option:

   `console_attach_ssh_args=""`

4. On the proxy host, SELinux should be customized:
  ```console
  # semanage port -a -t ovirt_vmconsole_proxy_port_t -p tcp XXX
  ```

5. On each affected virtualization host, SELinux should be customized as well:
  ```console
  # semanage port -a -t ovirt_vmconsole_host_port_t -p tcp XXX
  ```
