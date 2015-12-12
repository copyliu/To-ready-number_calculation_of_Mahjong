To-ready-number Calculation of Mahjong

---

## Project Introduction

This code is to calculate the to-ready-number of a mahjong hand. A ready hand's to-ready-number is 0, like 1112345678999m. A win hand's to-ready-number is -1. We'll support

> * Japanese Mahjong
> * Chinese National Standard (GB Mahjong)
> * Zung Jung Mahjong

---
## Japanese Mahjong

### Development Envrionment SetUp

* Development Software

    Please install the following software before. 

> * Python (2.7 preferred, not tested on 3 yet)

* Usage:
* Calculate all hands including regular, seven pairs and thirteen orphans:

```
./syanten.py -q $PAI (e.g.: 1112345678999m)
```

* Calculate regular hand only:

```
./syanten.py -p $PAI
```

* Only support 3*n+1, 3*n+2 tiles with n <= 4. When n < 3, only calculate regular hand.

* Reference:

> * http://mahjong.org
> * http://tenhou.net
