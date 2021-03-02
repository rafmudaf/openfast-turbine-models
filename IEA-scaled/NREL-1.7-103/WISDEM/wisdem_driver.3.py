from wisdem import run_wisdem
from wisdem.commonse.mpi_tools  import MPI
from helpers import load_yaml, save_yaml
import os, time, sys

istep = 3

## File management
run_dir = './'
fname_wt_input = os.path.join(run_dir, f'outputs.{istep-1}', f'NREL-1p7-103-step{istep-1}.yaml')
fname_modeling_options = os.path.join(run_dir, 'modeling_options_wisdem.yaml')
fname_analysis_options = os.path.join(run_dir, f'analysis_options.{istep}.yaml')

if MPI:
    rank = MPI.COMM_WORLD.Get_rank()
else:
    rank = 0

if rank == 0:
    print('STEP',istep)

    ## Update analysis options
    aopt = load_yaml(os.path.join(run_dir,'analysis_options.start.yaml'))
    aopt['general']['folder_output'] = f'outputs.{istep}'
    aopt['general']['fname_output'] = f'NREL-1p7-103-step{istep}'

    # - stall- and max-chord-constrained twist & chord opt for AEP
    aopt['driver']['optimization']['flag'] = True
    aopt['design_variables']['blade']['aero_shape']['twist']['flag'] = True
    aopt['design_variables']['blade']['aero_shape']['chord']['flag'] = True
    aopt['constraints']['blade']['stall']['flag'] = True
    aopt['constraints']['blade']['chord']['flag'] = True
    save_yaml(fname_analysis_options, aopt)

# Note: omega range does not get written out
# - decrease min rotor speed to avoid pitching in Region 1.5
# - increase max rotor speed for smaller rotor
model_changes = {
    'control.minOmega': 0.0, # [rad/s] ~= 5 RPM, don't pitch in Region 1.5
    'control.maxOmega': 1.6504854369, # [rad/s] == 15.8 RPM ==> Vtip = 85 m/s
}

tt = time.time()

wt_opt, modeling_options, opt_options = run_wisdem(
    fname_wt_input,
    fname_modeling_options,
    fname_analysis_options,
    overridden_values=model_changes,
)
 
if rank == 0:
    print('Run time: %f'%(time.time()-tt))
    sys.stdout.flush()