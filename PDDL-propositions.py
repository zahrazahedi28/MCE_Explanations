import pddlpy


template = """
(define (domain blocksworld)
  (:requirements :strips)
(:predicates (clear ?x)
             (on-table ?x)
             (arm-empty)
             (holding ?x)
             (on ?x ?y))

%OPERATORS%"""


#####################################################################
# get_predicates(action, human_model)
# -------------------------------------------------------------------
#####################################################################
def get_predicates(action, model_name):

    final = []

    for eff_prec in ["effect", "precondition"]:

        if eff_prec == "effect":
            operator = model_name+".domain.operators[action].effect"
        else:
            operator = model_name+".domain.operators[action].precondition"

        pos_neg_precs = []
        for add_del in ["add", "del"]:
            preds = []
            if add_del == "add":
                list_eff = eval(operator+"_pos")
            else:
                list_eff = eval(operator+"_neg")

            for atom in list_eff:
                pred = atom.predicate
                aux = ""
                for i in pred:
                    aux += "_" + i

                preds.append("action_"+action+"_has_"+add_del+"_"+eff_prec+aux)
            pos_neg_precs.append(preds)
        final.append(pos_neg_precs)

    return final


#####################################################################
# pddl_to_propositions()
# -------------------------------------------------------------------
#####################################################################
def pddl_to_propositions(actions, human_model):
    for action in actions:

        [pos_eff, neg_eff], [pos_prec, neg_prec] = get_predicates(action, human_model)

    return [pos_eff, neg_eff], [pos_prec, neg_prec]


#####################################################################
# def propositions_to_pddl(actions, pos_eff, neg_eff, pos_prec, neg_prec)
# -------------------------------------------------------------------
#####################################################################
def propositions_to_pddl(propositions, parameters):
    actionList = {}
    for prop in propositions:
        aux = prop.split("_")
        action = aux[1]
        add_del = aux[3]
        effect_prec = aux[4]
        objects = " ".join(aux[5:])

        if not actionList.get(action):
            actionList[action] = {
                "parameters": " ".join(parameters[action]),
                "precondition": [],
                "negprecondition": [],
                "add-effect": [],
                "delete-effect": []
            }

        if add_del == "add" and effect_prec == "precondition":
            actionList[action]['precondition'].append(objects)
        if add_del == "del" and effect_prec == "precondition":
            actionList[action]['negprecondition'].append(objects)
        if add_del == "add" and effect_prec == "effect":
            actionList[action]['add-effect'].append(objects)
        if add_del == "del" and effect_prec == "effect":
            actionList[action]['delete-effect'].append(objects)

    actionString = '\n'.join(['(:action {}\n  :parameters ({})\n  :precondition (and {})\n  :effect (and {}))\n'
                             .format(key, actionList[key]['parameters'],
                                     ''.join(['({}) '.format(p) for p in actionList[key]['precondition']]) + '' +
                                     ''.join(['(not ({})) '.format(p) for p in actionList[key]['negprecondition']]),
                                     '{}{}'.format(
                                         ''.join(['({}) '.format(p) for p in actionList[key]['add-effect']]),
                                         ''.join(
                                             ['(not ({})) '.format(p) for p in actionList[key]['delete-effect']]))) for
                              key in actionList.keys()])

    print(template.replace('%OPERATORS%',actionString))


if __name__ == '__main__':
    human_model = pddlpy.DomainProblem("blocks-domain.pddl", "prob2.pddl")
    actions = ["pickup", "putdown", "stack", "unstack"]
    model_name = "human_model"

    parameters = {}
    for action in actions:
        parameters[action] = list(human_model.domain.operators[action].variable_list.keys())

    test_propositions = ["action_stack_has_add_effect_clear_?ob",
         "action_stack_has_del_effect_clear_?ob",
         "action_pickup_has_add_effect_test_?ob"]

    [pos_eff, neg_eff], [pos_prec, neg_prec] = pddl_to_propositions(actions, model_name)
    propositions_to_pddl(test_propositions, parameters)