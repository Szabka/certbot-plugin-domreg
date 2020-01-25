# Certbot plugin for authentication using Domreg

This is a plugin for [Certbot](https://certbot.eff.org/) that uses the Domreg(domain.telekom.hu or domain.t-systems.hu) web portal to allow Telekom customers to prove control of a domain name.

## Usage

1. Install the plugin using `pip install certbot-plugin-domreg`

2. Create a `domreg.ini` config file with the following contents and apply `chmod 600 domreg.ini` on it:
   ```
   certbot_plugin_domreg:dns_passwd=DomregDomainPassword
   ```
   Replace `DomregDomainPassword` with your domain password and ensure permissions are set
   to disallow access to other users.

3. Run `certbot` and direct it to use the plugin for authentication and to use
   the config file previously created:
   ```
   certbot certonly -a certbot-plugin-domreg:dns --certbot-plugin-domreg:dns-credentials domreg.ini -d domain.com
   ```
   Add additional options as required to specify an installation plugin etc.

Huge thanks to Michael Porter and Yohann Leon for its original work!

## Distribution

## Wildcard certificates

This plugin is particularly useful when you need to obtain a wildcard certificate using dns challenges:

```
certbot certonly -a certbot-plugin-domreg:dns --certbot-plugin-domreg:dns-credentials domreg.ini -d domain.com -d \*.domain.com
```

## Automatic renewal

You can setup automatic renewal using `crontab` with the following job for weekly renewal attempts:

```
0 0 * * 0 certbot renew -q -a certbot-plugin-domreg:dns --certbot-plugin-domreg:dns-credentials /etc/letsencrypt/domreg/domreg.ini
```
