# M10 damage labelling protocol (draft)

Use the same definitions for (a) the people labelling the training/test photos and
(b) the interim vision-model assessor (`autocare/damage.py`), so both mean the same thing.
Have two people label every test photo independently and report their agreement (Cohen's kappa), per proposal §7.13.

## Severity (one per photo: the most damaged visible part)
- **Minor**: scratches, scuffs, paint chips or small dents; panel shape intact; no part broken or loose
- **Moderate**: clear dents or creases, a cracked or partly detached bumper cover, a broken lamp lens or mirror, damage across more than one panel; parts likely need repair or replacement but the body shape is intact
- **Severe**: crushed, torn or folded panels, deformed structure, doors or bonnet out of line, shattered glass, deployed airbags, or a wheel visibly pushed out of position.

## Body area (one per photo)
- `front_bumper`: Front bumper
- `rear_bumper`: Rear bumper
- `bonnet`: Bonnet
- `boot_lid`: Boot lid
- `roof`: Roof
- `windscreen`: Windscreen
- `rear_window`: Rear window
- `front_door`: Front door
- `rear_door`: Rear door
- `front_fender`: Front fender
- `rear_quarter_panel`: Rear quarter panel
- `headlamp`: Headlamp
- `tail_lamp`: Tail lamp
- `side_mirror`: Side mirror
- `wheel_rim`: Wheel / rim
- `side_skirt`: Side skirt
- `other`: Other body part

Side: `left` / `right` = driver's left/right facing forward; `centre`; `unknown` if you can't tell.

## Exclude or crop
- Number plates, faces, house numbers: crop them out before a photo enters the labelled set (proposal §9).
- Fluid leaks and the engine bay are out of scope: don't label them.
- No cost, fault or liability labels, ever.

## Label file (for the CNN, later)
`file,severity,location,side,labeller,source` (source = public dataset name + licence, or `team`).
