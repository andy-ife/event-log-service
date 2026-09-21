import MySQLdb
import uuid
import datetime

db = MySQLdb.connect(host="localhost", user="root", passwd="adminAdmin!123", db="openmrs", port=3306)
cursor = db.cursor()

datetimenow = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

sql = "select DISTINCT concept_id from concept_name where name = 'Offline Concepts'"
def isOfflineConceptsAlreadyPresent( sql ):
    db = MySQLdb.connect(host="localhost", user="root", passwd="adminAdmin!123", db="openmrs", port=3306)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results) > 0:
            return 1
        else:
            return 0
    except:
        return
    db.close()
    return

offlineConceptSetId = ""
if isOfflineConceptsAlreadyPresent(sql) == 0:
    conceptUuid = str(uuid.uuid1())
    insertConcept = "INSERT into concept (retired, datatype_id, class_id, is_set, creator, date_created, uuid) VALUES (0,1,10,1,1,'"+ datetimenow +"', '" + conceptUuid + "');"
    getConceptId = "SELECT concept_id from concept where uuid = '" + conceptUuid + "'"

    db = MySQLdb.connect(host="localhost", user="root", passwd="adminAdmin!123", db="openmrs", port=3306)
    cursor = db.cursor()
    try:
        cursor.execute(insertConcept)
        db.commit()
        cursor.execute(getConceptId)
        results = cursor.fetchall()
        offlineConceptSetId = str(results[0][0])
        insertConceptName = "insert into concept_name (concept_id, name, locale, creator, date_created, concept_name_type, voided, uuid) VALUES (" + offlineConceptSetId +", 'Offline Concepts','en', 1, '"+datetimenow+"', 'FULLY_SPECIFIED', 0, '" + str(uuid.uuid1()) +"');"
        print(insertConceptName)
        cursor.execute(insertConceptName)
        db.commit()
    except:
        print("")
    db.close()
else:
    db = MySQLdb.connect(host="localhost", user="root", passwd="adminAdmin!123", db="openmrs", port=3306)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        offlineConceptSetId = str(results[0][0])
    except:
        print("")
    db.close()



def insertConceptToOfflineConcepts( conceptId, conceptUuid, conceptName ):
    db = MySQLdb.connect(host="localhost", user="root", passwd="adminAdmin!123", db="openmrs", port=3306)
    cursor = db.cursor()
    query = "select count(concept_set_id) from concept_set where concept_id = "+ str(conceptId) + " and concept_set = " + offlineConceptSetId;
    cursor.execute(query)
    results = cursor.fetchall()
    if results[0][0] == 0:
        print(conceptName + " added to Offline Concept")
        query1 = "insert into concept_set (concept_id, concept_set, creator, date_created, uuid) values ("+ str(conceptId)+", "+ offlineConceptSetId +", 1, '"+datetimenow+"', '"+ str(uuid.uuid1()) +"')";
        uri = "/openmrs/ws/rest/v1/concept/" + conceptUuid + "?s=byFullySpecifiedName&v=bahmni&name="+conceptName
        query2 = "insert into event_records (uuid, title, timestamp, uri, object, category, date_created) VALUES ('"+str(uuid.uuid1())+"', 'Offline Concepts', '"+datetimenow+"', '"+uri+"', '"+uri+"', 'offline-concepts', '"+datetimenow+"')";
        try:
            cursor.execute(query1)
            db.commit()
            cursor.execute(query2)
            db.commit()
        except:
            print("")
        db.close()

concepts = []

def getAllConcepts(conceptId) :
    db = MySQLdb.connect(host="localhost", user="root", passwd="adminAdmin!123", db="openmrs", port=3306)
    cursor = db.cursor()
    query = "select concept_id from concept_set where concept_set = "+str(conceptId)+";"
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            concepts.append(row[0])
            getAllConcepts(row[0])
    except:
        print("")

def getConceptDetails(conceptId) :
    conceptDetails = []
    query = "select c.uuid, cn.name from concept c, concept_name cn where c.concept_id = cn.concept_id and cn.concept_name_type = 'FULLY_SPECIFIED' and c.concept_id = "+str(conceptId)+";"
    db = MySQLdb.connect(host="localhost", user="root", passwd="adminAdmin!123", db="openmrs", port=3306)
    cursor = db.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conceptDetails.append(results[0][0])
        conceptDetails.append(results[0][1])
    except:
        print("")
    return conceptDetails

def execute() :
    for index in range(len(concepts)):
        conceptDetails = getConceptDetails(concepts[index])
        uuid = conceptDetails[0]
        name = conceptDetails[1].replace(" ", "+")
        insertConceptToOfflineConcepts(concepts[index], uuid, name)

def getAllObsConceptId() :
    query = "select DISTINCT concept_id from concept_name where name = 'All Observation Templates'"
    db = MySQLdb.connect(host="localhost", user="root", passwd="adminAdmin!123", db="openmrs", port=3306)
    cursor = db.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    except:
        print("")
    return results[0][0]

allObsId = getAllObsConceptId()
concepts.append(allObsId)
getAllConcepts(allObsId)
execute()
