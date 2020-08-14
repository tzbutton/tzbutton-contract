TZButton.io SmartContract
====================================

Build/Basic Usage
-----------------

### Dependencies

This project depends only on SmartPy, you can install SmartPy by doing a:

```
$ curl -s https://SmartPy.io/dev/cli/SmartPy.sh -o /tmp/SmartPy.sh
$ chmod +x /tmp/SmartPy.sh
$ /tmp/SmartPy.sh local-install-auto smartpy
```

### Build

```
$ ./smartpy/SmartPy.sh compile tzbutton.py "TZButton()" out
```

### Test
```
$ ./smartpy/SmartPy.sh test tzbutton.py out
```