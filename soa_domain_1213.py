
WLHOME      = '/opt/oracle/middleware12c/wlserver'

DOMAIN      = 'soa_domain'
DOMAIN_PATH = '/opt/oracle/wlsdomains/domains/soa_domain'
APP_PATH    = '/opt/oracle/wlsdomains/applications/soa_domain'

SERVER_ADDRESS = '10.10.10.21'
LOG_FOLDER     = '/var/log/weblogic/'

JSSE_ENABLED     = true
DEVELOPMENT_MODE = true
WEBTIER_ENABLED  = false

ADMIN_SERVER   = 'AdminServer'
ADMIN_USER     = 'weblogic'
ADMIN_PASSWORD = 'weblogic1'

JAVA_HOME      = '/usr/java/latest'

ADM_JAVA_ARGUMENTS = '-XX:PermSize=256m -XX:MaxPermSize=512m -Xms1024m -Xmx1532m -Dweblogic.Stdout='+LOG_FOLDER+'AdminServer.out -Dweblogic.Stderr='+LOG_FOLDER+'AdminServer_err.out'
OSB_JAVA_ARGUMENTS = '-XX:PermSize=256m -XX:MaxPermSize=512m -Xms1024m -Xmx1024m -Dweblogic.Stdout='+LOG_FOLDER+'osb_server1.out -Dweblogic.Stderr='+LOG_FOLDER+'osb_server1_err.out'
SOA_JAVA_ARGUMENTS = '-XX:PermSize=256m -XX:MaxPermSize=752m -Xms1024m -Xmx1532m -Dweblogic.Stdout='+LOG_FOLDER+'soa_server1.out -Dweblogic.Stderr='+LOG_FOLDER+'soa_server1_err.out'
BAM_JAVA_ARGUMENTS = '-XX:PermSize=256m -XX:MaxPermSize=512m -Xms1024m -Xmx1532m -Dweblogic.Stdout='+LOG_FOLDER+'bam_server1.out -Dweblogic.Stderr='+LOG_FOLDER+'bam_server1_err.out'


SOA_REPOS_DBURL          = 'jdbc:oracle:thin:@soadb.example.com:1521/soarepos.example.com'
SOA_REPOS_DBUSER_PREFIX  = 'DEV'
SOA_REPOS_DBPASSWORD     = 'Welcome01'

BPM_ENABLED=true
BAM_ENABLED=true
B2B_ENABLED=true
ESS_ENABLED=true

def createBootPropertiesFile(directoryPath,fileName, username, password):
  serverDir = File(directoryPath)
  bool = serverDir.mkdirs()
  fileNew=open(directoryPath + '/'+fileName, 'w')
  fileNew.write('username=%s\n' % username)
  fileNew.write('password=%s\n' % password)
  fileNew.flush()
  fileNew.close()

def createAdminStartupPropertiesFile(directoryPath, args):
  adminserverDir = File(directoryPath)
  bool = adminserverDir.mkdirs()
  fileNew=open(directoryPath + '/startup.properties', 'w')
  args=args.replace(':','\\:')
  args=args.replace('=','\\=')
  fileNew.write('Arguments=%s\n' % args)
  fileNew.flush()
  fileNew.close()

print('Start...wls domain with template /opt/oracle/middleware12c/wlserver/common/templates/wls/wls.jar')
readTemplate('/opt/oracle/middleware12c/wlserver/common/templates/wls/wls.jar')


cd('/')

print('Set domain log')
create('base_domain','Log')

cd('/Log/base_domain')
set('FileName'    ,LOG_FOLDER+DOMAIN+'.log')
set('FileCount'   ,10)
set('FileMinSize' ,5000)
set('RotationType','byTime')
set('FileTimeSpan',24)

cd('/Servers/AdminServer')
# name of adminserver
set('Name',ADMIN_SERVER )

cd('/Servers/'+ADMIN_SERVER)

# address and port
set('ListenAddress',SERVER_ADDRESS)
set('ListenPort'   ,7001)

setOption( "AppDir", APP_PATH )

create(ADMIN_SERVER,'ServerStart')
cd('ServerStart/'+ADMIN_SERVER)
set('Arguments' , ADM_JAVA_ARGUMENTS)
set('JavaVendor','Sun')
set('JavaHome'  , JAVA_HOME)

cd('/Server/'+ADMIN_SERVER)
create(ADMIN_SERVER,'SSL')
cd('SSL/'+ADMIN_SERVER)
set('Enabled'                    , 'False')
set('HostNameVerificationIgnored', 'True')

if JSSE_ENABLED == true:
  set('JSSEEnabled','True')
else:
  set('JSSEEnabled','False')


cd('/Server/'+ADMIN_SERVER)

create(ADMIN_SERVER,'Log')
cd('/Server/'+ADMIN_SERVER+'/Log/'+ADMIN_SERVER)
set('FileName'    ,LOG_FOLDER+ADMIN_SERVER+'.log')
set('FileCount'   ,10)
set('FileMinSize' ,5000)
set('RotationType','byTime')
set('FileTimeSpan',24)

print('Set password...')
cd('/')
cd('Security/base_domain/User/weblogic')

# weblogic user name + password
set('Name',ADMIN_USER)
cmo.setPassword(ADMIN_PASSWORD)

if DEVELOPMENT_MODE == true:
  setOption('ServerStartMode', 'dev')
else:
  setOption('ServerStartMode', 'prod')

setOption('JavaHome', JAVA_HOME)

print('write domain...')
# write path + domain name
writeDomain(DOMAIN_PATH)
closeTemplate()

createAdminStartupPropertiesFile(DOMAIN_PATH+'/servers/'+ADMIN_SERVER+'/data/nodemanager',ADM_JAVA_ARGUMENTS)
createBootPropertiesFile(DOMAIN_PATH+'/servers/'+ADMIN_SERVER+'/security','boot.properties',ADMIN_USER,ADMIN_PASSWORD)
createBootPropertiesFile(DOMAIN_PATH+'/config/nodemanager','nm_password.properties',ADMIN_USER,ADMIN_PASSWORD)

es = encrypt(ADMIN_PASSWORD,DOMAIN_PATH)

readDomain(DOMAIN_PATH)

print('set domain password...') 
cd('/SecurityConfiguration/'+DOMAIN)
set('CredentialEncrypted',es)

print('Set nodemanager password')
set('NodeManagerUsername'         ,ADMIN_USER )
set('NodeManagerPasswordEncrypted',es )

cd('/')

setOption( "AppDir", APP_PATH )

print('Extend...osb domain with template /opt/oracle/middleware12c/osb/common/templates/wls/oracle.osb_template_12.1.3.jar')
addTemplate('/opt/oracle/middleware12c/oracle_common/common/templates/wls/oracle.wls-webservice-template_12.1.3.jar')
addTemplate('/opt/oracle/middleware12c/osb/common/templates/wls/oracle.osb_template_12.1.3.jar')

print 'Adding ApplCore Template'
addTemplate('/opt/oracle/middleware12c/oracle_common/common/templates/wls/oracle.applcore.model.stub.1.0.0_template.jar')

print 'Adding SOA Template'
addTemplate('/opt/oracle/middleware12c/soa/common/templates/wls/oracle.soa_template_12.1.3.jar')

if BAM_ENABLED == true:
  print 'Adding BAM Template'
  addTemplate('/opt/oracle/middleware12c/soa/common/templates/wls/oracle.bam.server_template_12.1.3.jar')

if BPM_ENABLED == true:
  print 'Adding BPM Template'
  addTemplate('/opt/oracle/middleware12c/soa/common/templates/wls/oracle.bpm_template_12.1.3.jar')

if WEBTIER_ENABLED == true:
  print 'Adding OHS Template'
  addTemplate('/opt/oracle/middleware12c/ohs/common/templates/wls/ohs_managed_template_12.1.3.jar')

if B2B_ENABLED == true:
  print 'Adding B2B Template'
  addTemplate('/opt/oracle/middleware12c/soa/common/templates/wls/oracle.soa.b2b_template_12.1.3.jar')

if ESS_ENABLED == true:
  print 'Adding ESS Template'
  addTemplate('/opt/oracle/middleware12c/oracle_common/common/templates/wls/oracle.ess.basic_template_12.1.3.jar')
  addTemplate('/opt/oracle/middleware12c/em/common/templates/wls/oracle.em_ess_template_12.1.3.jar')

dumpStack()

print 'Change datasources'

print 'Change datasource LocalScvTblDataSource'
cd('/JDBCSystemResource/LocalSvcTblDataSource/JdbcResource/LocalSvcTblDataSource/JDBCDriverParams/NO_NAME_0')
set('URL',SOA_REPOS_DBURL)
set('PasswordEncrypted',SOA_REPOS_DBPASSWORD)
cd('Properties/NO_NAME_0/Property/user')
set('Value',SOA_REPOS_DBUSER_PREFIX+'_STB')

print 'Call getDatabaseDefaults which reads the service table'
getDatabaseDefaults()    

print 'Change datasource EDNDataSource'
cd('/JDBCSystemResource/EDNDataSource/JdbcResource/EDNDataSource/JDBCDriverParams/NO_NAME_0')
set('DriverName','oracle.jdbc.xa.client.OracleXADataSource')
set('UseXADataSourceInterface','True') 
cd('/JDBCSystemResource/EDNDataSource/JdbcResource/EDNDataSource/JDBCDataSourceParams/NO_NAME_0')
set('GlobalTransactionsProtocol','TwoPhaseCommit')

print 'Change datasource wlsbjmsrpDataSource'
cd('/JDBCSystemResource/wlsbjmsrpDataSource/JdbcResource/wlsbjmsrpDataSource/JDBCDriverParams/NO_NAME_0')
set('DriverName','oracle.jdbc.xa.client.OracleXADataSource')
set('UseXADataSourceInterface','True') 
cd('/JDBCSystemResource/wlsbjmsrpDataSource/JdbcResource/wlsbjmsrpDataSource/JDBCDataSourceParams/NO_NAME_0')
set('GlobalTransactionsProtocol','TwoPhaseCommit')

print 'Change datasource OraSDPMDataSource'
cd('/JDBCSystemResource/OraSDPMDataSource/JdbcResource/OraSDPMDataSource/JDBCDriverParams/NO_NAME_0')
set('DriverName','oracle.jdbc.xa.client.OracleXADataSource')
set('UseXADataSourceInterface','True') 
cd('/JDBCSystemResource/OraSDPMDataSource/JdbcResource/OraSDPMDataSource/JDBCDataSourceParams/NO_NAME_0')
set('GlobalTransactionsProtocol','TwoPhaseCommit')

print 'Change datasource SOADataSource'
cd('/JDBCSystemResource/SOADataSource/JdbcResource/SOADataSource/JDBCDriverParams/NO_NAME_0')
set('DriverName','oracle.jdbc.xa.client.OracleXADataSource')
set('UseXADataSourceInterface','True') 
cd('/JDBCSystemResource/SOADataSource/JdbcResource/SOADataSource/JDBCDataSourceParams/NO_NAME_0')
set('GlobalTransactionsProtocol','TwoPhaseCommit')

if BAM_ENABLED == true:
  print 'Change datasource BamDataSource'
  cd('/JDBCSystemResource/BamDataSource/JdbcResource/BamDataSource/JDBCDriverParams/NO_NAME_0')
  set('DriverName','oracle.jdbc.xa.client.OracleXADataSource')
  set('UseXADataSourceInterface','True') 
  cd('/JDBCSystemResource/BamDataSource/JdbcResource/BamDataSource/JDBCDataSourceParams/NO_NAME_0')
  set('GlobalTransactionsProtocol','TwoPhaseCommit')

print 'end datasources'

print 'Add server groups WSM-CACHE-SVR WSMPM-MAN-SVR JRF-MAN-SVR to AdminServer'
serverGroup = ["WSM-CACHE-SVR" , "WSMPM-MAN-SVR" , "JRF-MAN-SVR"]
setServerGroups(ADMIN_SERVER, serverGroup)                      

if ESS_ENABLED == true:
  print 'Add server group SOA-MGD-SVRS,ESS-MGD-SVRS to soa_server1'
  cd('/')
  delete('ess_server1', 'Server')
  serverGroup = ["SOA-MGD-SVRS","ESS-MGD-SVRS"]
else:
  print 'Add server group SOA-MGD-SVRS to soa_server1'
  serverGroup = ["SOA-MGD-SVRS"]

setServerGroups('soa_server1', serverGroup)                      

if BAM_ENABLED == true:
  print 'Add server group BAM12-MGD-SVRS to bam_server1'
  serverGroup = ["BAM12-MGD-SVRS"]
  setServerGroups('bam_server1', serverGroup)                      

print 'Add server group OSB-MGD-SVRS-COMBINED to osb_server1'
serverGroup = ["OSB-MGD-SVRS-COMBINED"]
setServerGroups('osb_server1', serverGroup)                      

print 'end server groups'

updateDomain()
closeDomain();


readDomain(DOMAIN_PATH)

if BAM_ENABLED == true:
  print 'change BAM/BPM ForeignJNDIProviders'
  cd('/')
  cd('/ForeignJNDIProvider/BAMForeignJndiProvider')
  set('ProviderURL','t3://'+SERVER_ADDRESS+':9001')

  cd('/ForeignJNDIProvider/BPMForeignJndiProvider')
  set('ProviderURL','t3://'+SERVER_ADDRESS+':8001')
  print 'end BAM/BPM ForeignJNDIProviders'

print('Create machine LocalMachine with type UnixMachine')
cd('/')
create('LocalMachine','UnixMachine')
cd('UnixMachine/LocalMachine')
create('LocalMachine','NodeManager')
cd('NodeManager/LocalMachine')
set('ListenAddress',SERVER_ADDRESS)

print 'Change AdminServer'
cd('/Servers/'+ADMIN_SERVER)
set('Machine','LocalMachine')


print 'Change soa_server1'

setOption( "AppDir", APP_PATH )

cd('/Servers/soa_server1')
set('Machine'      ,'LocalMachine')
set('ListenAddress',SERVER_ADDRESS)
set('ListenPort'   ,8001)

create('soa_server1','ServerStart')
cd('ServerStart/soa_server1')
set('Arguments' , SOA_JAVA_ARGUMENTS)
set('JavaVendor','Sun')
set('JavaHome'  , JAVA_HOME)

cd('/Server/soa_server1')
create('soa_server1','SSL')
cd('SSL/soa_server1')
set('Enabled'                    , 'False')
set('HostNameVerificationIgnored', 'True')

if JSSE_ENABLED == true:
  set('JSSEEnabled','True')
else:
  set('JSSEEnabled','False')

cd('/Server/soa_server1')
create('soa_server1','Log')
cd('/Server/soa_server1/Log/soa_server1')
set('FileName'     , LOG_FOLDER+'soa_server1.log')
set('FileCount'    , 10)
set('FileMinSize'  , 5000)
set('RotationType' ,'byTime')
set('FileTimeSpan' , 24)

if BAM_ENABLED == true:
  print 'Change bam_server1'
  cd('/Servers/bam_server1')
  set('Machine'      ,'LocalMachine')
  set('ListenAddress',SERVER_ADDRESS)
  set('ListenPort'   ,9001)

  create('bam_server1','ServerStart')
  cd('ServerStart/bam_server1')
  set('Arguments' , BAM_JAVA_ARGUMENTS)
  set('JavaVendor','Sun')
  set('JavaHome'  , JAVA_HOME)

  cd('/Server/bam_server1')
  create('bam_server1','SSL')
  cd('SSL/bam_server1')
  set('Enabled'                    , 'False')
  set('HostNameVerificationIgnored', 'True')

  if JSSE_ENABLED == true:
    set('JSSEEnabled','True')
  else:
    set('JSSEEnabled','False')

  cd('/Server/bam_server1')
  create('bam_server1','Log')
  cd('/Server/bam_server1/Log/bam_server1')
  set('FileName'    ,LOG_FOLDER+'bam_server1.log')
  set('FileCount'   ,10)
  set('FileMinSize' ,5000)
  set('RotationType','byTime')
  set('FileTimeSpan',24)


print 'Change osb_server1'
cd('/Servers/osb_server1')
set('Machine'      ,'LocalMachine')
set('ListenAddress',SERVER_ADDRESS)
set('ListenPort'   ,8011)

create('osb_server1','ServerStart')
cd('ServerStart/osb_server1')
set('Arguments' , OSB_JAVA_ARGUMENTS)
set('JavaVendor','Sun')
set('JavaHome'  , JAVA_HOME)

cd('/Server/osb_server1')
create('osb_server1','SSL')
cd('SSL/osb_server1')
set('Enabled'                    , 'False')
set('HostNameVerificationIgnored', 'True')

if JSSE_ENABLED == true:
  set('JSSEEnabled','True')
else:
  set('JSSEEnabled','False')

cd('/Server/osb_server1')
create('osb_server1','Log')
cd('/Server/osb_server1/Log/osb_server1')
set('FileName'    ,LOG_FOLDER+'osb_server1.log')
set('FileCount'   ,10)
set('FileMinSize' ,5000)
set('RotationType','byTime')
set('FileTimeSpan',24)

dumpStack()
updateDomain()
closeDomain()

createBootPropertiesFile(DOMAIN_PATH+'/servers/soa_server1/security','boot.properties',ADMIN_USER,ADMIN_PASSWORD)

if BAM_ENABLED == true:
  createBootPropertiesFile(DOMAIN_PATH+'/servers/bam_server1/security','boot.properties',ADMIN_USER,ADMIN_PASSWORD)

createBootPropertiesFile(DOMAIN_PATH+'/servers/osb_server1/security','boot.properties',ADMIN_USER,ADMIN_PASSWORD)

print('Exiting...')
exit()
