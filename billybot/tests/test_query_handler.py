import unittest

from billybot.query_handler import VoteQuery


class TestVoteQuery(unittest.TestCase):

    messages = {0: "Sorry, I wasn't able to find matches for",
                1: "Sorry, your query is not properly formatted"}

    def get_message(cls, msg_num, str_to_append=None):
        msg = cls.messages[msg_num]
        if str_to_append:
            msg = msg + ' ' + str_to_append
        return msg

    def setUp(self):
        message = "member: Warren bill: S.Con.Res.3"
        self.errors, self.resp = VoteQuery.query_setup(message)

    def test_run_query(self):
        print ("HEYIEROIEROI")
        message = "member: Warren bill: S.Con.Res.3"
        vote_query, reply, attachment = VoteQuery.run_query(message)
        self.assertIn('member: Warren bill: S.Con.Res.3', repr(vote_query))
        self.assertIn("I found multiple matches", reply)

    def test_query_setup(self):
        self.assertFalse(self.errors)
        self.assertIn("member: Warren bill: S.Con.Res.3", repr(self.resp))

    def test_query_errors(self):
        message = "member: Gontar bill: S.Con.Res.3"
        self.errors, self.resp = VoteQuery.query_setup(message)
        self.assertTrue(self.errors)
        expected_resp = self.get_message(0, "'Gontar'")
        self.assertEqual(self.resp, expected_resp)

        message = "Gontar bill: S.Con.Res.3"
        self.errors, self.resp = VoteQuery.query_setup(message)
        expected_resp = self.get_message(1)
        self.assertEqual(self.resp, expected_resp)

    def test_parse_query(self):
        vote_query = self.resp
        self.assertEqual(vote_query.query_data['member'], 'Warren')
        self.assertEqual(vote_query.query_data['bill_votes'], 'S.Con.Res.3')

    def test_initialize_params(self):
        vote_query = self.resp
        self.assertFalse(vote_query.initialize_params())
        message = "member: Gontar bill: S.Con.Res.3"
        vote_query = VoteQuery(message)
        vote_query.query_data['member'] = 'Gontar'
        vote_query.query_data['bill_votes'] = 'S.Con.Res.3'
        errors = vote_query.initialize_params()
        self.assertIn("Gontar", errors)

    def test_bill_results_data_gathered_correctly(self):
        vote_query = self.resp
        title = vote_query.results_data['bill_title']
        expected_title = "A concurrent resolution setting forth the "\
                         "congressional budget for the United States "\
                         "Government for fiscal year 2017 and setting "\
                         "forth the appropriate budgetary levels for "\
                         "fiscal years 2018 through 2026."
        self.assertEqual(title, expected_title)
        bill_id = vote_query.results_data['bill_id']
        expected_bill_id = 'sconres3-115'
        self.assertEqual(bill_id, expected_bill_id)
        bill_chamber = vote_query.results_data['bill_chamber']
        expected_bill_chamber = 'senate'
        self.assertEqual(bill_chamber, expected_bill_chamber)
        bill_url = vote_query.results_data['bill_url']
        expected_bill_url = "https://www.congress.gov/bill/"\
                            "115th/senate-concurrent-resolution/3"
        self.assertEqual(bill_url, expected_bill_url)

    def test_set_member_results_data(self):
        vote_query = self.resp
        vote_query.set_member_results_data('W000817')

        member_name = vote_query.results_data['member_name']
        expected_name = "Sen. Elizabeth Warren (D-MA)"
        self.assertEqual(member_name, expected_name)
        member_title = vote_query.results_data['member_title']
        expected_title = "Sen"
        self.assertEqual(member_title, expected_title)
        member_chamber = vote_query.results_data['member_chamber']
        expected_chamber = "senate"
        self.assertEqual(member_chamber, expected_chamber)
        member_party = vote_query.results_data['member_party']
        expected_party = "D"
        self.assertEqual(member_party, expected_party)
        member_state = vote_query.results_data['member_state']
        expected_state = "MA"
        self.assertEqual(member_state, expected_state)
        member_url = vote_query.results_data['member_url']
        expected_url = "http://www.warren.senate.gov"
        self.assertEqual(member_url, expected_url)

    def test_set_roll_vote_data(self):
        vote_query = self.resp
        self.assertNotIn('roll_id', vote_query.results_data.keys())
        vote_query.set_roll_vote_data('s26-2017')

        roll_id = vote_query.results_data['roll_id']
        expected_roll_id = "s26-2017"
        self.assertEqual(roll_id, expected_roll_id)
        roll_question = vote_query.results_data['roll_question']
        expected_question = "On the Concurrent Resolution S.Con.Res. 3"
        self.assertEqual(roll_question, expected_question)
        roll_url = vote_query.results_data['roll_url']
        expected_roll_url = "http://www.senate.gov/legislative/"\
                            "LIS/roll_call_lists/roll_call_vote_cfm.cfm"\
                            "?congress=115&session=1&vote=00026"
        self.assertEqual(roll_url, expected_roll_url)

    def test_resolve_query(self):
        vote_query = self.resp
        vote_query.search_parameters['member'] = "W000817"
        vote_query.results_data['member_name'] = "Sen. Elizabeth Warren (D-MA)"
        vote_query.search_parameters['bill_votes'] = "s26-2017"
        result = vote_query.resolve_query()
        expected_result = "Sen. Elizabeth Warren (D-MA) voted Nay on s26-2017."
        self.assertEqual(result, expected_result)
