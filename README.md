# disneyland-reservation-checker
Check reservation availability at Disneyland and California Adventure

## Options
`-s` query start date as yyyy-mm-dd

`-e` query end date as yyyy-mm-dd

## Usage
To search reservation availability for a single day, use the `-s` flag
```shell
disneyland_reservation_checker.py -s 2021-11-03
```
To search reservation availability for a range of days, use both the `-s` and
`-e` flags
```shell
disneyland_reservation_checker.py -s 2021-12-01 -e 2021-12-31
```
