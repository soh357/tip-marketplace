<kibana_address>/app/kibana#/discover?_g=(time:(from:'<from_time>',mode:absolute,to:'<to_time>'))&_a=(columns:!(level,fields.CustomFields.Component,fields.CustomFields.Module,message),filters:!(),query:(language:lucene,query:'(_index:smp_server%5C*%20OR%20_index:smp_etl%5C*)%20AND%20level:%22Error%22%20AND%20fields.CustomFields.Component:%22Playbooks%22'),sort:!('@timestamp',desc))