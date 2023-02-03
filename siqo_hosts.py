#==============================================================================
# Siqo common library settings
#------------------------------------------------------------------------------

hosts = {
      "ODS": {
         "HOST"    : "dbprod44-scan.tatrabanka.sk",
         "PORT"    : "1521",
         "SERVICE" : "TRN_USERS.tatrabanka.sk",
         "SERV_ID" : 22
      },
    
      "IALFONZ": {
         "HOST"    : "oradbintl2.tatrabanka.sk",
         "PORT"    : "1523",
         "SERVICE" : "IALFONZ.TATRABANKA.SK",
         "SERV_ID" : 2
      },
      "UALFONZ": {
         "HOST"    : "oradbuatl2.tatrabanka.sk",
         "PORT"    : "1522",
         "SERVICE" : "UALFONZ.TATRABANKA.SK",
         "SERV_ID" : 2
      },
      "ALFONZ": {
         "HOST"    : "oradbprodl2.tatrabanka.sk",
         "PORT"    : "1521",
         "SERVICE" : "ALFONZ.tatrabanka.sk",
         "SERV_ID" : 2
      },
    
      "DDWH": {
         "HOST"    : "oradbdevl1.tatrabanka.sk", 
         "PORT"    : "1525",
         "SERVICE" : "DDWH.TATRABANKA.SK",
         "SERV_ID" : 1
      },
      "IDWH": {
         "HOST"    : "oradbintl1.tatrabanka.sk",
         "PORT"    : "1523",
         "SERVICE" : "IDWH_USERS.TATRABANKA.SK",
         "SERV_ID" : 1
      },
      "UDWH": {
         "HOST"    : "oradbuatl1.tatrabanka.sk",
         "PORT"    : "1522",
         "SERVICE" : "UDWH_USERS.TATRABANKA.SK",
         "SERV_ID" : 1
      },
      "DWH": {
         "HOST"    : "oradbprodl1.tatrabanka.sk", 
         "PORT"    : "1521",
         "SERVICE" : "DWH_USERS.tatrabanka.sk",
         "SERV_ID" : 1
      },
      "Neo4j": {
         "HOST"    : "neo4j://10.238.168.57", 
         "PORT"    : "7687",
         "SERVICE" : "Neo4j",
         "SERV_ID" : "NEO"
      },
      "TBLAKE": {
         "HOST"    : "", 
         "PORT"    : "",
         "SERVICE" : "TBLAKE",
         "SERV_ID" : "TBLAKE"
      }
      
}


#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print('SIQO hosts library ver 1.01')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------