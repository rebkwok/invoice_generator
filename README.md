# Invoice generator

Generates simple one-item invoices.

Create a config file, using  `config_template.ini` as a guide. Each customer should have a 
separate config file set up with billing details. Sections in the config file can
optionally be used to generate invoices for different services for the same customer, by
overriding any config from the `DEFAULT` section.

```
Usage: generate_invoices.py [OPTIONS]

Options:
  -c, --config PATH          Location of config file; defaults to 'config.ini' in current directory
  -t, --type TEXT            Invoice type; must correspond to a section in config.ini
  -i, --invoice-num INTEGER  Invoice number to start at; defaults to 1
  -d, --dates TEXT           Invoice dates, in YYYYMMDD format
  --help                     Show this message and exit.
```

