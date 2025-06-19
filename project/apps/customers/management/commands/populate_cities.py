from django.core.management.base import BaseCommand
from ...models import City

class Command(BaseCommand):
    help = 'Populate database with Algerian wilayas'

    def handle(self, *args, **options):
        # List of Algerian wilayas with their postal codes
        wilayas = [
            {'name': 'Adrar', 'code': '001-0100'},
            {'name': 'Chlef', 'code': '002-0200'},
            {'name': 'Laghouat', 'code': '003-0300'},
            {'name': 'Oum El Bouaghi', 'code': '004-0400'},
            {'name': 'Batna', 'code': '005-0500'},
            {'name': 'Béjaïa', 'code': '006-0600'},
            {'name': 'Biskra', 'code': '007-0700'},
            {'name': 'Béchar', 'code': '008-0800'},
            {'name': 'Blida', 'code': '009-0900'},
            {'name': 'Bouira', 'code': '010-1000'},
            {'name': 'Tamanrasset', 'code': '011-1100'},
            {'name': 'Tébessa', 'code': '012-1200'},
            {'name': 'Tlemcen', 'code': '013-1300'},
            {'name': 'Tiaret', 'code': '014-1400'},
            {'name': 'Tizi Ouzou', 'code': '015-1500'},
            {'name': 'Alger', 'code': '016-1600'},
            {'name': 'Djelfa', 'code': '017-1700'},
            {'name': 'Jijel', 'code': '018-1800'},
            {'name': 'Sétif', 'code': '019-1900'},
            {'name': 'Saïda', 'code': '020-2000'},
            {'name': 'Skikda', 'code': '021-2100'},
            {'name': 'Sidi Bel Abbès', 'code': '022-2200'},
            {'name': 'Annaba', 'code': '023-2300'},
            {'name': 'Guelma', 'code': '024-2400'},
            {'name': 'Constantine', 'code': '025-2500'},
            {'name': 'Médéa', 'code': '026-2600'},
            {'name': 'Mostaganem', 'code': '027-2700'},
            {'name': 'M\'Sila', 'code': '028-2800'},
            {'name': 'Mascara', 'code': '029-2900'},
            {'name': 'Ouargla', 'code': '030-3000'},
            {'name': 'Oran', 'code': '031-3100'},
            {'name': 'El Bayadh', 'code': '032-3200'},
            {'name': 'Illizi', 'code': '033-3300'},
            {'name': 'Bordj Bou Arréridj', 'code': '034-3400'},
            {'name': 'Boumerdès', 'code': '035-3500'},
            {'name': 'El Tarf', 'code': '036-3600'},
            {'name': 'Tindouf', 'code': '037-3700'},
            {'name': 'Tissemsilt', 'code': '038-3800'},
            {'name': 'El Oued', 'code': '039-3900'},
            {'name': 'Khenchela', 'code': '040-4000'},
            {'name': 'Souk Ahras', 'code': '041-4100'},
            {'name': 'Tipaza', 'code': '042-4200'},
            {'name': 'Mila', 'code': '043-4300'},
            {'name': 'Aïn Defla', 'code': '044-4400'},
            {'name': 'Naâma', 'code': '045-4500'},
            {'name': 'Aïn Témouchent', 'code': '046-4600'},
            {'name': 'Ghardaïa', 'code': '047-4700'},
            {'name': 'Relizane', 'code': '048-4800'},
            {'name': 'El M\'Ghair', 'code': '049-4900'},
            {'name': 'El Meniaa', 'code': '050-5000'},
            {'name': 'Ouled Djellal', 'code': '051-5100'},
            {'name': 'Bordj Baji Mokhtar', 'code': '052-5200'},
            {'name': 'Béni Abbès', 'code': '053-5300'},
            {'name': 'Timimoun', 'code': '054-5400'},
            {'name': 'Touggourt', 'code': '055-5500'},
            {'name': 'Djanet', 'code': '056-5600'},
            {'name': 'In Salah', 'code': '057-5700'},
            {'name': 'In Guezzam', 'code': '058-5800'},
        ]

        # Counter for created and updated records
        created_count = 0
        updated_count = 0

        for wilaya in wilayas:
            # Try to get existing city or create new one
            city, created = City.objects.update_or_create(
                name=wilaya['name'],
                defaults={'code': wilaya['code']}
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated database with {len(wilayas)} Algerian wilayas. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )