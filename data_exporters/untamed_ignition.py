from mage_ai.orchestration.triggers.api import trigger_pipeline
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

from mage_ai.data_preparation.shared.secrets import get_secret_value


@data_exporter
def trigger(risk_score, *args, **kwargs):
    """
    Trigger another Mage pipeline to run.

    Documentation: https://docs.mage.ai/orchestration/triggers/trigger-pipeline
    """
    get_secret_value('SECRETTTTTTTTTTTTTTT')

    trigger_pipeline(
        'calculat_ltv',
        variables={
            'risk_score': risk_score,
        },
    )

