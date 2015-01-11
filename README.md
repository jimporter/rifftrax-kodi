RiffTrax for Kodi
===================

This is an add-on for Kodi (aka XBMC) to organize locally-stored RiffTrax
videos. Eventually, it will support streaming from rifftrax.com, and might even
support commentary .mp3 files.

Development
-----------

The actual source for the add-on is in `plugin.video.rifftrax/`. To make
development easier, there are `make` commands to install/uninstall the add-on
from your local XBMC instance:

```
make install-dev
make uninstall-dev
```

Packaging
---------

To package the add-on into a .zip file for release, just run:

```
make package
```

License
-------

This add-on is licensed under the BSD 3-clause license.
