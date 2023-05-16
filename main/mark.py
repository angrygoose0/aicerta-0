import os
import openai
import re

openai.api_key = os.getenv('AI_API')
from .models import NceaExam, NceaQUESTION, Specifics, NceaSecondaryQuestion, NceaUserDocument, NceaUserQuestions
class Marking:
    @staticmethod
    def mark(id):
        doc = NceaDocument.objects.get(id=id)
        qs = NceaQuestions.objects.filter(document = doc)
        two = NceaTwo.objects.filter(exam=doc.exam)
        
        
        for q in qs:
            answer=q.text
            a = two.get(QUESTION=q.QUESTION, primary=q.primary, secondary=q.secondary)
            achieved = a.achieved
            merit = a.merit
            excellence = a.excellence
            
            bbb ="""
            QUESTION ONE
            Assesment Schedule:

            Achieved: 
            • Identifies the correct
            number of bonding and
            non-bonding regions for
            ONE molecule.
            • Recognises electron
            density regions arranged
            in position of max
            separation / min
            repulsion.

            Merit: 
            • Links total number of
            bonding regions to parent
            geometry and bond angle
            for ONE molecule using
            repulsion theory. 

            Excellence:
            • Justifies shape of both molecules
            with reference to all relevant
            factors.

            Answer:
            Freon-11 has 4 regions of electron density around the central carbon
            atom, while sulfur dioxide has 3 regions around the central sulfur atom.
            In both molecules these regions of electron density repel to maximum
            separation. This gives freon-11 a tetrahedral parent geometry and bond
            angles of 109.5°, while sulfur dioxide has a parent geometry of trigonal
            planar and bond angles of 120°. As all regions in freon-11 are bonding
            regions the overall shape is tetrahedral, while in sulfur dioxide two of the
            regions are bonding regions, while one is non-bonding, giving it an
            overall shape of bent.

            Mark the answer above using the assement schedule, one bullet point is one point.
            Points: 2 Achieved, 1 Merit, 1 Excellence


            QUESTION TWO
            Assesment Schedule:

            Achieved:
            • Describes structure
            of diamond.
            OR
            Graphite.
            • Identifies mobile free
            charged particles are
            required for
            conductivity.

            Merit:
            • Links conductivity /
            non-conductivity to
            presence / absence of
            free valence electrons
            in substance.

            Excellence:
            • Comprehensively explains
            conductivity of diamond
            and graphite.

            Answer:
            In order to conduct electricity, a substance must possess charged particles that are
            free to move.
            Diamond is made up of a 2D covalent network. Each carbon is bonded to 4 others. This means there
            are no valence electrons free to move throughout the structure, and diamond does
            not conduct electricity.
            Graphite is a 3d-covalent network substance. It consists of layers of carbon atoms,
            bound in hexagonal rings by strong covalent bonds. Each carbon is bonded to 3
            others. This means there are (delocalised) valence electrons free to move
            throughout the structure, allowing graphite to conduct electricity.

            Mark the answer above using the assement schedule, one bullet point is one point.
            Points: 1 Achieved, 1 Merit, 1 Excellence

            QUESTION THREE
            Assesment Schedule:

            Achieved: 
            • Identifies a difference in electronegativity between atoms in bonds.

            Merit:
            • Links symmetry / asymmetry of molecule to cancellation / noncancellation of dipoles in ONE molecule.

            Excellence:
            
            
            Answer:
            sdfghjkhgfdsdfghjhgfdsfghjfdfgh

            Points: 0 Achieved, 0 Merit, 0 Excellence


            QUESTION FOUR
            Assesment Schedule:

            Achieved: 
            {}

            Merit:
            {}

            Excellence:
            {}

            Answer:
            {}

            Points: _Achieved, _Merit, _Excellence
            """.format(achieved, merit, excellence, answer)
            
            retrieve = openai.Completion.create(model="text-davinci-003", prompt=bbb, temperature=0.2, max_tokens=256)
            x = (retrieve['choices'][0]['text'])
            no = re.findall(r'\d+', x)
            a = int(no[0])
            m = int(no[1])
            e = int(no[2])
            q.mark = "%s%s%s" % (a, m, e)