# Prometheus Node Exporter

This is a packaging of the standard Prometheus node_exporter: https://github.com/prometheus/node_exporter

Some of the standard OSes have this package but it is a very old version. This packages the specified version with a given systemd unit file for running the service.

## Update node_exporter

To update this build to a newer version:

1. Update the verion at the to of `./download_new_version.sh` to desired verison
2. Run `./download_new_version.sh`. This script will grab the binary for supported architectures.
3. Update `unibuild-packaging/rpm/prometheus-node-exporter.spec` with the new version number
4. Update `unibuild-packaging/deb/changelog` with the new version number
5. Commit you changes to git.

That's it! You should be good to build with unibuild.

## Note on Package Naming

The package generated will be named *prometheus-node-exporter*. This is the standard Debian name. The Prometheus project also provides an RPM called `node_exporter`. Unfortunately the underscore in this name is not compliant with Debian package naming. As such the generated RPM is named prometheus-node-exporter to make life easier for unibuild, but Provides node_exporter so this will override the default one if available as an older version.

