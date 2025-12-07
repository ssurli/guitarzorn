"""
Script per testare tutti i 5 approcci e generare le opere
Esegui con: python test_all_approaches.py
"""

import sys
import time

print("🎨 GUITARZORN - Test di tutti gli approcci")
print("=" * 60)
print()

approaches = [
    {
        'name': 'Energy Field',
        'file': 'approach_1_energy_field.py',
        'description': 'Esplosioni energetiche radiali, distribuite organicamente',
        'best_for': 'Riff energici, rock, punk'
    },
    {
        'name': 'Layered Transparency',
        'file': 'approach_2_layered_transparency.py',
        'description': 'Campi di colore sovrapposti, stile Rothko/Color Field',
        'best_for': 'Ballad, ambient, musica atmosferica'
    },
    {
        'name': 'Particle System',
        'file': 'approach_3_particle_system.py',
        'description': 'Sistemi di particelle esplosive, molto dinamico',
        'best_for': 'Metal, shred, tecnica virtuosistica'
    },
    {
        'name': 'Organic Growth',
        'file': 'approach_4_organic_growth.py',
        'description': 'Crescita organica tipo forme botaniche',
        'best_for': 'Jazz, fusion, musica progressiva'
    },
    {
        'name': 'Tension Field',
        'file': 'approach_5_tension_field.py',
        'description': 'Tensione armonica → tensione visiva con linee di forza',
        'best_for': 'Musica concettuale, visualizzazione teorica'
    }
]

for i, approach in enumerate(approaches, 1):
    print(f"\n[{i}/5] Generando: {approach['name']}")
    print(f"    Descrizione: {approach['description']}")
    print(f"    Ideale per: {approach['best_for']}")
    print(f"    Eseguendo {approach['file']}...")

    try:
        # Importa ed esegue
        start_time = time.time()

        if approach['file'] == 'approach_1_energy_field.py':
            from approach_1_energy_field import EnergyFieldArt
            artist = EnergyFieldArt()
            artist.create_artwork()
        elif approach['file'] == 'approach_2_layered_transparency.py':
            from approach_2_layered_transparency import LayeredTransparencyArt
            artist = LayeredTransparencyArt()
            artist.create_artwork()
        elif approach['file'] == 'approach_3_particle_system.py':
            from approach_3_particle_system import ParticleSystemArt
            artist = ParticleSystemArt()
            artist.create_artwork()
        elif approach['file'] == 'approach_4_organic_growth.py':
            from approach_4_organic_growth import OrganicGrowthArt
            artist = OrganicGrowthArt()
            artist.create_artwork()
        elif approach['file'] == 'approach_5_tension_field.py':
            from approach_5_tension_field import TensionFieldArt
            artist = TensionFieldArt()
            artist.create_artwork()

        elapsed = time.time() - start_time
        print(f"    ✅ Completato in {elapsed:.2f}s")

    except Exception as e:
        print(f"    ❌ Errore: {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 60)
print("✨ Tutti gli approcci sono stati generati!")
print()
print("File generati:")
print("  - energy_field_art.png")
print("  - layered_transparency_art.png")
print("  - particle_system_art.png")
print("  - organic_growth_art.png")
print("  - tension_field_art.png")
print()
print("Ora puoi confrontare visivamente i risultati!")
