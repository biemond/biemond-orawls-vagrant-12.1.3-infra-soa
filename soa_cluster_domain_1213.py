
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
OSB_JAVA_ARGUMENTS = '-XX:PermSize=256m -XX:MaxPermSize=512m -Xms1024m -Xmx1024m '
SOA_JAVA_ARGUMENTS = '-XX:PermSize=256m -XX:MaxPermSize=752m -Xms1024m -Xmx1532m '
BAM_JAVA_ARGUMENTS = '-XX:PermSize=256m -XX:MaxPermSize=512m -Xms1024m -Xmx1532m '


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

def changeDatasourceToXA(datasource):
  print 'Change datasource '+datasource
  cd('/')
  cd('/JDBCSystemResource/'+datasource+'/JdbcResource/'+datasource+'/JDBCDriverParams/NO_NAME_0')
  set('DriverName','oracle.jdbc.xa.client.OracleXADataSource')
  set('UseXADataSourceInterface','True') 
  cd('/JDBCSystemResource/'+datasource+'/JdbcResource/'+datasource+'/JDBCDataSourceParams/NO_NAME_0')
  set('GlobalTransactionsProtocol','TwoPhaseCommit')
  cd('/')

def changeManagedServer(server,port,java_arguments):
  cd('/Servers/'+server)
  set('Machine'      ,'LocalMachine')
  set('ListenAddress',SERVER_ADDRESS)
  set('ListenPort'   ,port)

  create(server,'ServerStart')
  cd('ServerStart/'+server)
  set('Arguments' , java_arguments+' -Dweblogic.Stdout='+LOG_FOLDER+server+'.out -Dweblogic.Stderr='+LOG_FOLDER+server+'_err.out')
  set('JavaVendor','Sun')
  set('JavaHome'  , JAVA_HOME)

  cd('/Server/'+server)
  create(server,'SSL')
  cd('SSL/'+server)
  set('Enabled'                    , 'False')
  set('HostNameVerificationIgnored', 'True')

  if JSSE_ENABLED == true:
    set('JSSEEnabled','True')
  else:
    set('JSSEEnabled','False')  

  cd('/Server/'+server)
  create(server,'Log')
  cd('/Server/'+server+'/Log/'+server)
  set('FileName'     , LOG_FOLDER+server+'.log')
  set('FileCount'    , 10)
  set('FileMinSize'  , 5000)
  set('RotationType' ,'byTime')
  set('FileTimeSpan' , 24)



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

changeDatasourceToXA('EDNDataSource')
changeDatasourceToXA('wlsbjmsrpDataSource')
changeDatasourceToXA('OraSDPMDataSource')
changeDatasourceToXA('SOADataSource')

if BAM_ENABLED == true:
  changeDatasourceToXA('BamDataSource')

print 'end datasources'

setOption( "AppDir", APP_PATH )

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

cd('/')
if ESS_ENABLED == true:
  delete('ess_server1', 'Server')

if BAM_ENABLED == true:
  delete('bam_server1', 'Server')

delete('soa_server1', 'Server')
delete('osb_server1', 'Server')


print 'Create SoaCluster'
cd('/')
create('SoaCluster', 'Cluster')

print 'Create SoaServer1'
cd('/')
create('SoaServer1', 'Server')
changeManagedServer('SoaServer1',8001,SOA_JAVA_ARGUMENTS)

print 'Create SoaServer2'
cd('/')
create('SoaServer2', 'Server')
changeManagedServer('SoaServer2',8002,SOA_JAVA_ARGUMENTS)

cd('/')
assign('Server','SoaServer1','Cluster','SoaCluster')
assign('Server','SoaServer2','Cluster','SoaCluster')

if BAM_ENABLED == true:
  print 'Create BamCluster'
  cd('/')
  create('BamCluster', 'Cluster')

  print 'Create BamServer1'
  cd('/')
  create('BamServer1', 'Server')
  changeManagedServer('BamServer1',9001,BAM_JAVA_ARGUMENTS)

  print 'Create BamServer2'
  cd('/')
  create('BamServer2', 'Server')
  changeManagedServer('BamServer2',9002,BAM_JAVA_ARGUMENTS)

  cd('/')
  assign('Server','BamServer1','Cluster','BamCluster')
  assign('Server','BamServer2','Cluster','BamCluster')

print 'Create OsbCluster'
cd('/')
create('OsbCluster', 'Cluster')

print 'Create OsbServer1'
cd('/')
create('OsbServer1', 'Server')
changeManagedServer('OsbServer1',8011,OSB_JAVA_ARGUMENTS)

print 'Create OsbServer2'
cd('/')
create('OsbServer2', 'Server')
changeManagedServer('OsbServer2',8012,OSB_JAVA_ARGUMENTS)

cd('/')
assign('Server','OsbServer1','Cluster','OsbCluster')
assign('Server','OsbServer2','Cluster','OsbCluster')


print 'Add server groups WSM-CACHE-SVR WSMPM-MAN-SVR JRF-MAN-SVR to AdminServer'
serverGroup = ["WSM-CACHE-SVR" , "WSMPM-MAN-SVR" , "JRF-MAN-SVR"]
setServerGroups(ADMIN_SERVER, serverGroup)                      

if ESS_ENABLED == true:
  print 'Add server group SOA-MGD-SVRS,ESS-MGD-SVRS to soa_server1'
  cd('/')
  serverGroup = ["SOA-MGD-SVRS","ESS-MGD-SVRS"]
else:
  print 'Add server group SOA-MGD-SVRS to SoaServer1 2'
  serverGroup = ["SOA-MGD-SVRS"]

setServerGroups('SoaServer1', serverGroup)                      
setServerGroups('SoaServer2', serverGroup)                      

if BAM_ENABLED == true:
  print 'Add server group BAM12-MGD-SVRS to BamServer1 2'
  serverGroup = ["BAM12-MGD-SVRS"]
  setServerGroups('BamServer1', serverGroup)                      
  setServerGroups('BamServer2', serverGroup)                      

print 'Add server group OSB-MGD-SVRS-COMBINED to OsbServer1 2'
serverGroup = ["OSB-MGD-SVRS-COMBINED"]
setServerGroups('OsbServer1', serverGroup)                      
setServerGroups('OsbServer2', serverGroup)                      

print 'end server groups'

updateDomain()
closeDomain();

createBootPropertiesFile(DOMAIN_PATH+'/servers/SoaServer1/security','boot.properties',ADMIN_USER,ADMIN_PASSWORD)
createBootPropertiesFile(DOMAIN_PATH+'/servers/SoaServer2/security','boot.properties',ADMIN_USER,ADMIN_PASSWORD)

if BAM_ENABLED == true:
  createBootPropertiesFile(DOMAIN_PATH+'/servers/BamServer1/security','boot.properties',ADMIN_USER,ADMIN_PASSWORD)
  createBootPropertiesFile(DOMAIN_PATH+'/servers/BamServer2/security','boot.properties',ADMIN_USER,ADMIN_PASSWORD)

createBootPropertiesFile(DOMAIN_PATH+'/servers/OsbServer1/security','boot.properties',ADMIN_USER,ADMIN_PASSWORD)
createBootPropertiesFile(DOMAIN_PATH+'/servers/OsbServer2/security','boot.properties',ADMIN_USER,ADMIN_PASSWORD)

print('Exiting...')
exit()
