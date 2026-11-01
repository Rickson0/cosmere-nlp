from src.util.ontology_loader import load_ontology

def staff_members():
    membros_nomes = {}
    
    staff = load_ontology('data/ontology/staff.yaml')
    for people in staff['staff']:
        if people['active']:
            nome = people['name'].lower()
            membros_nomes[nome] = nome.lower() 
            for alias in people['aliases']:
                membros_nomes[alias] = nome.lower()

    return membros_nomes