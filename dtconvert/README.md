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
`[p]tz  7:20 pm America/Los Angeles`
`[p]tz  03.12.2020 21:00 pm CET`
`[p]tz  03.12.2020 21:00 pm +01:00`


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