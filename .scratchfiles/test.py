import json
jdata = '{"results":[{"bioguide_id":"D000626","birthday":"1970-03-01","chamber":"house","contact_form":null,"crp_id":"N00038767","district":8,"fax":null,"fec_ids":["H6OH08315"],"first_name":"Warren","gender":"M","govtrack_id":"412675","in_office":true,"last_name":"Davidson","leadership_role":null,"middle_name":null,"name_suffix":null,"nickname":null,"oc_email":"Rep.Davidson@opencongress.org","ocd_id":"ocd-division/country:us/state:oh/cd:8","office":"1004 Longworth House Office Building","party":"R","phone":"202-225-6205","state":"OH","state_name":"Ohio","term_end":"2019-01-03","term_start":"2017-01-03","thomas_id":"02296","title":"Rep","votesmart_id":166760,"website":"https://davidson.house.gov"},{"bioguide_id":"W000817","birthday":"1949-06-22","chamber":"senate","contact_form":"http://www.warren.senate.gov/?p=email_senator#thisForm","crp_id":"N00033492","district":null,"facebook_id":"131559043673264","fax":null,"fec_ids":["S2MA00170"],"first_name":"Elizabeth","gender":"F","govtrack_id":"412542","icpsr_id":41301,"in_office":true,"last_name":"Warren","leadership_role":null,"lis_id":"S366","middle_name":null,"name_suffix":null,"nickname":null,"oc_email":"Sen.Warren@opencongress.org","ocd_id":"ocd-division/country:us/state:ma","office":"317 Hart Senate Office Building","party":"D","phone":"202-224-4543","senate_class":1,"state":"MA","state_name":"Massachusetts","state_rank":"senior","term_end":"2019-01-03","term_start":"2013-01-03","thomas_id":"02182","title":"Sen","twitter_id":"SenWarren","votesmart_id":141272,"website":"http://www.warren.senate.gov","youtube_id":"senelizabethwarren"}],"count":2,"page":{"count":2,"per_page":20,"page":1}}'

results = json.loads(jdata)['results']

def outer(data):
    def inner(bio_id, request):
        member = next((bio for bio in data if bio.get('bioguide_id') == bio_id))
        return member.get(request)
    matches = [(item['first_name'], item['last_name'], item['bioguide_id']) for item in data]
    return inner, matches

retriever, options = outer(results)
print('Here are your options:\n', options)
choice = int(input('> ')) - 1

d = options[choice]

print(retriever(d[2], 'oc_email'))

