# DateTimeConvert

Convert date & time between timezones

## Conversion:
`[p]tz <date> <time> <timezone>`
where `[p]` is your command prefix

`<date>` is either the US (mm/dd/yyyy) or the European notation (dd.mm.yyyy).

`<time>` can be given in the 24h- or 12h clock.

`<timezone>` is either an abbreviation like EDT, an identifier like Europe/London, or an UTC offset like +10:00.

Check https://en.wikipedia.org/wiki/List_of_time_zone_abbreviations and https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for details.

### Examples
`[p]tz 12/03/2020 9:00 pm EST`
```
2020-12-04 02:00 ( 2:00 am) UTC 
2020-12-03 18:00 ( 6:00 pm) PST 
2020-12-03 21:00 ( 9:00 pm) EST 
2020-12-04 02:00 ( 2:00 am) GMT
2020-12-04 13:00 ( 1:00 pm) AEDT
```

`[p]tz  7:20 pm America/Los Angeles`
```
02:20 ( 2:20 am) +1 day UTC 
19:20 ( 7:20 pm) +0 day PDT 
22:20 (10:20 pm) +0 day EDT 
03:20 ( 3:20 am) +1 day BST 
12:20 (12:20 pm) +1 day AEST
```

`[p]tz  03.12.2020 21:00 CET`
```
2020-12-03 20:00 ( 8:00 pm) UTC 
2020-12-03 12:00 (12:00 pm) PST 
2020-12-03 15:00 ( 3:00 pm) EST 
2020-12-03 20:00 ( 8:00 pm) GMT 
2020-12-04 07:00 ( 7:00 am) AEDT
```

`[p]tz  03.12.2020 21:00 +01:00`
```
2020-12-03 20:00 ( 8:00 pm) UTC 
2020-12-03 12:00 (12:00 pm) PST 
2020-12-03 15:00 ( 3:00 pm) EST 
2020-12-03 20:00 ( 8:00 pm) GMT
2020-12-04 07:00 ( 7:00 am) AEDT
```


## Personal timezone
If configured, you can set a timezone with
`[p]tz me <timezone>`

If you have one set, you can omit it when you run a command like `[p]tz tz 12/03/2020 9:00 pm` and it will assume your timezone.


## For admins
Show, add, and remove output timezones with
`[p]dtconvert list`
`[p]dtconvert add`
`[p]dtconvert remove`

Include UTC in the output
`[p]dtconvert showutc [True/False]`

Enable user timezones
`[p]dtconvert usertimezones [True/False]`