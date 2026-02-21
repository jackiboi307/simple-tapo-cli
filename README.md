# simple-tapo-cli

A dead simple TP-Link Tapo CLI, using Python and the `tapo` module. In theory it supports any Tapo lamp that `tapo` supports, but currently it is hardcoded to use the L530 (or some similar device like the L535).

It supports changing the brightness (or turning the lamp off by setting it to 0), setting it to a certain temperature or a color using hue and saturation. Values are either set or incremented / decremented, see below.

Expected ranges: 0-100 for brightness, 0-360 for hue, 1-100 for saturation, and 2500-6500 for temperature. Values that are out of range are clamped, except for when it comes to hue, which wraps around instead.

```bash
$ tapo b=0  # keys can be shortened ('br', 'bright' etc. are also valid)
$ tapo hue=0 sat=100
$ tapo hue+10
$ tapo hue-10
$ tapo temp=3000  # a warm white
```
