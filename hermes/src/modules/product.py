import csv
import networkx as nx

from hermes.src.utils.utils import _getDelimiter

setting_cache = {}

def _get_setting(setting, name):
	if name not in setting_cache:
		setting_cache[name] = setting(name)

	return setting_cache[name]

def _percent_diff(a, b):
	if abs(a+b) < 0.0001:
		return 1
	return 2*abs(a-b)/(a+b)

def _not_null(val):
	if not val or val == 'NA' or val == '0.00' or val == '0':
		return False
	return True

def _is_not_price(key, setting):
	if key in _get_setting(setting, 'price_columns') or key in _get_setting(setting, 'msrp_columns') or key in _get_setting(setting, 'cost_columns'):
		return False

	return True

def _compute_score(a, b, attr, setting):
	score = 0
	for key in _get_setting(setting, 'must_match'):
		if key in attr[a] and (attr[a][key] != attr[b][key]):
			return 0

	# non-float values
	for key, val in attr[a].iteritems():
		if key in attr[b]:
			if _is_not_price(key, setting):
				if attr[b][key] == val:
					score += 1
	# price values
	for price_name in ['price_columns', 'msrp_columns', 'cost_columns']:
		columns = _get_setting(setting, price_name)
		if type(columns) == type('str'):
			columns = [columns]

		comparables = [_percent_diff(float(attr[a][key]), float(attr[b][key])) 
								for key in columns if key in attr[a]]
		if not comparables:
			continue

		max_sim = max(comparables)

		if max_sim < _get_setting(setting, 'max_diff'):
			score += 1

	return score

def getGraph(file_name, setting):
	G = nx.Graph()
	properties = {}
	node_attr = {}

	with open(file_name, 'r') as csv_file:
		reader = csv.reader(csv_file, delimiter=_getDelimiter(setting), quotechar=setting('quotechar'))
		keys = []
		for i, row in enumerate(reader):
			print i
			if i == 0:
				keys = row
				continue
			prod = i
			node_attr[prod] = {}
			sim = []
			for j, val in enumerate(row):
				key = keys[j]
				if _not_null(val):
					if _is_not_price(key, setting):
						prop_key = key+'-'+val
						if key in _get_setting(setting, 'must_match'):
							if prop_key not in properties:
								properties[prop_key] = []
							else:
								sim = set(list(sim) + properties[prop_key])
							properties[prop_key].append(prod)

					node_attr[prod][key] = val
				else:
					node_attr[prod][key] = 0

			G.add_node(prod, node_attr[prod])

			for sim_node in sim:
				w = _compute_score(sim_node, prod, node_attr, setting)
				if w == 0:
					continue
				G.add_edge(sim_node, prod, weight=w)


			# if i > 40:
			# 	break

	return G