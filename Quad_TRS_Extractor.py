for site in sites:

	management.SelectLayerByAttribute("Quadrangle_Index", "NEW_SELECTION", "OBJECTID = {}".format(site[0]))
	management.SelectLayerByLocation("PLSSTownship", "INTERSECT", "Quadrangle_Index", '', "NEW_SELECTION")
	management.SelectLayerByLocation("PLSSTownship", "INTERSECT", "Footprint_12152017", '', "SUBSET_SELECTION")
     
	tr = []

	with da.SearchCursor("PLSSTownship", ["OBJECTID", "TWNSHPLAB"]) as cursor:
	 for row in cursor:
		 tr.append([row[0], row[1]])

	for t in tr:
         
		management.SelectLayerByAttribute("PLSSTownship", "NEW_SELECTION", "OBJECTID = {}".format(t[0]))
		management.SelectLayerByLocation("PLSSFirstDivision", "HAVE_THEIR_CENTER_IN", "PLSSTownship", '', "NEW_SELECTION")
		management.SelectLayerByLocation("PLSSFirstDivision", "INTERSECT", "Footprint_12152017", '', "SUBSET_SELECTION")

		sections = []

		with da.SearchCursor("PLSSFirstDivision", "FRSTDIVLAB") as cursor:
		 for row in cursor:
			 sections.append(row[0])
			 
		sections = sorted(sections)

		dict = {
		"Quadrangle Name" : site[1],
		"Township/Range" : t[1],
		"Sections" : ', '.join(sections),
		}

		dictlist.append(dict)

		management.SelectLayerByAttribute("PLSSFirstDivision", "CLEAR_SELECTION")
