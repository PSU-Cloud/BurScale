// Copyright 2018 The Loadcat Authors. All rights reserved.

package data

type Vmtype string

var Vmtypes = []Vmtype{
	"ondemand",
	"burst",

}

func (a Vmtype) Label() string {
	return VmtypeLabels[a]
}

var VmtypeLabels = map[Vmtype]string{
	"ondemand":       "On Demand",
	"burst": "Burstable",

}
