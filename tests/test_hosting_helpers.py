"""Observable arithmetic/reconciliation/gate tests. No live provider or model behavior."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

def load(skill,script):
    p=ROOT/skill/'scripts'/script
    spec=importlib.util.spec_from_file_location(skill.replace('-','_'),p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def example(skill):return json.loads((ROOT/skill/'assets/example.json').read_text())

MENU='menu-prep-planner'; POT='potluck-signup-coordinator'; GIFT='gift-season-manager'; REM='event-reminder-lifecycle'
menu=load(MENU,'menu.py');pot=load(POT,'reconcile.py');gift=load(GIFT,'budget.py');rem=load(REM,'guard.py')

class MenuTests(unittest.TestCase):
    def setUp(self):self.d=example(MENU)
    def test_scale_subtract_reserved_stock(self):
        row=menu.report(self.d)['shopping'][0]
        self.assertEqual((row['required'],row['available'],row['buy']),('500','300','200'))
    def test_unknown_quantity_stays_unknown(self):self.assertEqual(len(menu.report(self.d)['unquantified']),1)
    def test_overlap_reported(self):self.assertEqual(menu.report(self.d)['resource_conflicts'][0]['resource'],'oven')
    def test_adjacent_not_overlap(self):
        self.d['bookings'][1]['start']=self.d['bookings'][0]['end']
        self.assertEqual(menu.report(self.d)['resource_conflicts'],[])
    def test_offset_equivalent_overlap(self):
        self.d['bookings'][1]['start']='2026-12-21T00:30:00+00:00'
        self.assertTrue(menu.report(self.d)['resource_conflicts'])
    def test_mass_volume_and_preparation_separate(self):
        items=self.d['recipes'][0]['ingredients'];items.pop()
        for unit,prep in [('ml','plain-all-purpose'),('g','wholegrain')]:
            items.append({'ingredient_id':'flour','preparation':prep,'quantity':'1','unit':unit})
        self.assertEqual(len(menu.report(self.d)['shopping']),3)
    def test_unit_conversion(self):
        self.d['recipes'][0]['ingredients'][0].update(quantity='0.25',unit='kg')
        self.assertEqual(menu.report(self.d)['shopping'][0]['buy'],'200.00')
    def test_reject_ambiguous_unit(self):
        self.d['recipes'][0]['ingredients'][0]['unit']='cup'
        with self.assertRaises(ValueError):menu.report(self.d)
    def test_reject_overreserved_stock(self):
        self.d['pantry'][0]['reserved']='501'
        with self.assertRaises(ValueError):menu.report(self.d)
    def test_reject_bad_numbers(self):
        for v in [True,0,-1,'NaN','Infinity',0.5]:
            with self.subTest(v=v),self.assertRaises(ValueError):
                d=deepcopy(self.d);d['target_servings']=v;menu.report(d)
    def test_reject_duplicate_booking(self):
        self.d['bookings'][1]['id']=self.d['bookings'][0]['id']
        with self.assertRaises(ValueError):menu.report(self.d)
    def test_reject_naive_booking(self):
        self.d['bookings'][0]['start']='2026-12-20T16:00:00'
        with self.assertRaises(ValueError):menu.report(self.d)

class PotluckTests(unittest.TestCase):
    def setUp(self):self.d=example(POT)
    def test_partial_absence_not_removal(self):
        r=pot.report(self.d);self.assertEqual(r['removed_claim_ids'],[]);self.assertEqual(r['missing_in_partial_claim_ids'],['c-1'])
    def test_complete_absence_observed_removal(self):
        self.d['after']['complete']=True;self.assertEqual(pot.report(self.d)['removed_claim_ids'],['c-1'])
    def test_partial_does_not_claim_verified_vacancy(self):
        row=pot.report(self.d)['coverage'][0]
        self.assertIsNone(row['open_units']);self.assertEqual(row['possible_open_units_upper_bound'],1)
    def test_overfill_units_not_people(self):
        c=deepcopy(self.d['before']['claims'][0]);c['id']='c-2';c['portions']=None
        self.d['after']['claims']=[deepcopy(self.d['before']['claims'][0]),c]
        r=pot.report(self.d)['coverage'][0]
        self.assertEqual((r['claimed_units'],r['known_portions'],r['unknown_portion_claims'],r['overfilled_units']),(2,8,1,1))
        self.assertFalse(r['coverage_complete'])
    def test_cancelled_does_not_fill(self):
        c=deepcopy(self.d['before']['claims'][0]);c['status']='cancelled';self.d['after']['claims']=[c]
        r=pot.report(self.d);self.assertEqual(r['explicitly_cancelled_claim_ids'],['c-1']);self.assertEqual(r['coverage'][0]['claimed_units'],0)
    def test_dish_edit_detected(self):
        self.d['after']=deepcopy(self.d['before']);self.d['after']['claims'][0]['dish']='Salad'
        self.assertEqual(pot.report(self.d)['changed_claim_ids'],['c-1'])
    def test_private_data_and_formula_not_executed_or_exported(self):
        self.d['after']=deepcopy(self.d['before']);self.d['after']['claims'][0].update(dish='=IMPORTXML("private")',email='secret@example.invalid',private_notes='SECRET')
        out=json.dumps(pot.report(self.d));self.assertNotIn('SECRET',out);self.assertNotIn('IMPORTXML',out);self.assertNotIn('@',out)
    def test_reject_duplicate_claim(self):
        self.d['after']['claims']=self.d['before']['claims']*2
        with self.assertRaises(ValueError):pot.report(self.d)
    def test_reject_unknown_slot(self):
        self.d['after']['claims']=deepcopy(self.d['before']['claims']);self.d['after']['claims'][0]['slot_id']='missing'
        with self.assertRaises(ValueError):pot.report(self.d)
    def test_reject_noninteger_units(self):
        for v in [True,-1,0,1.5,'1']:
            with self.subTest(v=v),self.assertRaises(ValueError):
                d=deepcopy(self.d);d['before']['claims'][0]['units']=v;pot.report(d)
    def test_require_completeness(self):
        del self.d['after']['complete']
        with self.assertRaises(ValueError):pot.report(self.d)

class GiftTests(unittest.TestCase):
    def setUp(self):self.d=example(GIFT)
    def test_no_deposit_double_count(self):
        r=gift.report(self.d);self.assertEqual((r['net_paid'],r['unpaid_commitments'],r['known_forecast'],r['headroom_against_known_costs']),('80.00','70.00','240.00','60.00'))
    def test_pending_refund_not_cash(self):
        self.d['costs'][0]['cancelled']=True;self.d['costs'][0]['refund_pending']='80'
        self.assertEqual(gift.report(self.d)['known_forecast'],'170.00')
    def test_received_refund(self):
        self.d['costs'][0].update(cancelled=True,refund_received='80')
        self.assertEqual(gift.report(self.d)['known_forecast'],'90.00')
    def test_unknown_not_zero(self):
        self.d['costs'][1]['estimate']=None;r=gift.report(self.d)
        self.assertFalse(r['complete']);self.assertEqual(r['unknown_cost_ids'],['cost-2'])
    def test_over_budget_negative_headroom(self):
        self.d['budget']='100';self.assertEqual(gift.report(self.d)['headroom_against_known_costs'],'-140.00')
    def test_reject_excess_refund(self):
        self.d['costs'][0]['refund_received']='81'
        with self.assertRaises(ValueError):gift.report(self.d)
    def test_reject_mixed_currency(self):
        self.d['costs'][0]['currency']='EUR'
        with self.assertRaises(ValueError):gift.report(self.d)
    def test_reject_duplicate_id(self):
        self.d['costs'][1]['id']='cost-1'
        with self.assertRaises(ValueError):gift.report(self.d)
    def test_reject_paid_without_commitment(self):
        self.d['costs'][0]['committed_total']=None
        with self.assertRaises(ValueError):gift.report(self.d)
    def test_reject_double_estimate(self):
        self.d['costs'][0]['estimate']='150'
        with self.assertRaises(ValueError):gift.report(self.d)
    def test_reject_invalid_money(self):
        for v in ['NaN','Infinity','-1','0.001',True,0.5]:
            with self.subTest(v=v),self.assertRaises(ValueError):
                d=deepcopy(self.d);d['budget']=v;gift.report(d)
    def test_recipient_data_never_in_output(self):
        self.d['costs'][0].update(recipient='PRIVATE',idea='SURPRISE',address='SECRET')
        out=json.dumps(gift.report(self.d))
        for v in ['PRIVATE','SURPRISE','SECRET']:self.assertNotIn(v,out)

class ReminderTests(unittest.TestCase):
    def setUp(self):
        self.d=example(REM);self.d.update(job_revision=2,now=self.d['due'])
    def test_exact_due_eligible(self):self.assertTrue(rem.decision(self.d)['eligible'])
    def test_exact_cutoff_expired(self):
        self.d['now']=self.d['cutoff'];self.assertEqual(rem.decision(self.d)['reason'],'expired')
    def test_early(self):
        self.d['now']='2026-12-20T16:00:00-08:00';self.assertEqual(rem.decision(self.d)['reason'],'not_due')
    def test_stale(self):
        self.d['job_revision']=1;self.assertEqual(rem.decision(self.d)['reason'],'superseded')
    def test_inactive(self):
        for state in ['cancelled','closed']:
            self.d['event_status']=state;self.assertEqual(rem.decision(self.d)['reason'],'event_inactive')
    def test_already_sent(self):
        self.d['already_sent']=True;self.assertEqual(rem.decision(self.d)['reason'],'already_sent')
    def test_task_done(self):
        self.d['task_complete']=True;self.assertEqual(rem.decision(self.d)['reason'],'task_complete')
    def test_offset_equivalence(self):
        self.d['now']='2026-12-21T01:00:00+00:00';self.assertTrue(rem.decision(self.d)['eligible'])
    def test_naive_time_rejected(self):
        self.d['now']='2026-12-20T17:00:00'
        with self.assertRaises(ValueError):rem.decision(self.d)
    def test_reject_empty_window(self):
        self.d['cutoff']=self.d['due']
        with self.assertRaises(ValueError):rem.decision(self.d)
    def test_reject_nonboolean(self):
        self.d['already_sent']='false'
        with self.assertRaises(ValueError):rem.decision(self.d)

class CliTests(unittest.TestCase):
    def test_each_example_executes_and_source_unchanged(self):
        for skill,script in [(MENU,'menu.py'),(POT,'reconcile.py'),(GIFT,'budget.py'),(REM,'guard.py')]:
            with self.subTest(skill=skill):
                p=ROOT/skill/'assets/example.json';before=p.read_bytes()
                r=subprocess.run([sys.executable,str(ROOT/skill/'scripts'/script),str(p)],capture_output=True,text=True)
                self.assertEqual(r.returncode,0,r.stderr);self.assertIsInstance(json.loads(r.stdout),dict);self.assertEqual(p.read_bytes(),before)
    def test_bad_input_cli_is_nonzero_no_stdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.json';p.write_text('{}')
            for skill,script in [(MENU,'menu.py'),(POT,'reconcile.py'),(GIFT,'budget.py'),(REM,'guard.py')]:
                with self.subTest(skill=skill):
                    r=subprocess.run([sys.executable,str(ROOT/skill/'scripts'/script),str(p)],capture_output=True,text=True)
                    self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'');self.assertIn('Invalid input:',r.stderr)

if __name__=='__main__':unittest.main()
