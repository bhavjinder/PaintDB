import csv
from Schema import OrthologEcoli, Interactor, Interaction, InteractionReference, InteractionSource

def parse(session):
    with open('Data/Ecoli/RegulonDB.csv') as csvfile:
        reader = csv.DictReader(csvfile)

        source = InteractionSource(data_source = 'RegulonDB(Ecoli)', is_experimental = 2)
        session.add(source), session.commit()

        for row in reader:
            interactors = []

            orthologs_A = session.query(OrthologEcoli).filter_by(
                ortholog_name = (row['TF name'][0].lower() + row['TF name'][1:])).all()
            orthologs_B = session.query(OrthologEcoli).filter_by(ortholog_name = row['Regulated gene']).all()

            for ortholog_A in orthologs_A:
                for ortholog_B in orthologs_B:
                    if (ortholog_A is not None) and (ortholog_B is not None) and \
                            (ortholog_A.strain_protein == ortholog_B.strain_protein):
                        interactors.append([[ortholog_A.protein, ortholog_A.ortholog_id],
                                            [ortholog_B.protein, ortholog_B.ortholog_id]])

            for interactor_pair in interactors:
                homogenous = (interactor_pair[0][0] == interactor_pair[1][0])
                interaction = session.query(Interaction).filter(Interaction.interactors.contains(interactor_pair[0][0]),
                                                                Interaction.interactors.contains(interactor_pair[1][0]),
                                                                Interaction.homogenous == homogenous).first()
                if interaction is None:
                    interaction = Interaction(strain=interactor_pair[0][0].strain,
                                              interactors=[interactor_pair[0][0], interactor_pair[1][0]], type='p-p',
                                              ortholog_derived='Ecoli')
                    session.add(interaction), session.commit()

                interactor_a, interactor_b = None, None
                if interaction.interactors[0] == interactor_pair[0][0]:
                    interactor_a = interactor_pair[0][1]
                    interactor_b = interactor_pair[1][1]
                else:
                    interactor_b = interactor_pair[0][1]
                    interactor_a = interactor_pair[1][1]

                type= 'TF/sigma-binding site (' + row['Regulatory effect'] + 'regulation)'
                comment= interactor_pair[0][1] + ' regulates(' +row['Regulatory effect'] + ') ' + interactor_pair[1][1]
                for evidence in row['Evidence'][1:-1].split(', '):
                    # check if interaction reference already exists in db
                    reference = session.query(InteractionReference).filter_by(detection_method = evidence,
                                                                              interaction_type = type,
                                                                              source_db = 'regulondb',
                                                                              confidence = row['Evidence type'],
                                                                              comment = comment,
                                                                              interactor_a = interactor_a,
                                                                              interactor_b = interactor_b).first()
                    if reference is None:
                        reference = InteractionReference(detection_method = evidence, interaction_type = type,
                                                         comment=comment, source_db='regulondb',
                                                         confidence = row['Evidence type'],
                                                         interactor_a=interactor_a, interactor_b=interactor_b)
                        interaction.references.append(reference)
                        reference.sources.append(source)
                    else:
                        if interaction not in reference.interactions:
                            interaction.references.append(reference)
                        if source not in reference.sources:
                            reference.sources.append(source)

                if source not in interaction.sources:
                    interaction.sources.append(source)

    session.commit()
    print('regulondb', session.query(Interaction).count())