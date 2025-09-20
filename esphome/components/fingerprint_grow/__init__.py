from esphome import automation, pins
import esphome.codegen as cg
from esphome.components import uart
import esphome.config_validation as cv
from esphome.const import (
    CONF_COLOR,
    CONF_COUNT,
    CONF_FINGER_ID,
    CONF_ID,
    CONF_NEW_PASSWORD,
    CONF_NUM_SCANS,
    CONF_PASSWORD,
    CONF_SENSING_PIN,
    CONF_SPEED,
    CONF_STATE,
    CONF_TRIGGER_ID,
)

CODEOWNERS = ["@OnFreund", "@loongyh", "@alexborro"]
DEPENDENCIES = ["uart"]
AUTO_LOAD = ["binary_sensor", "sensor"]
MULTI_CONF = True

CONF_FINGERPRINT_GROW_ID = "fingerprint_grow_id"
CONF_SENSOR_POWER_PIN = "sensor_power_pin"
CONF_IDLE_PERIOD_TO_SLEEP = "idle_period_to_sleep"

CONF_ON_SLEEP_ENTER = "on_sleep_enter"
CONF_ON_SLEEP_EXIT = "on_sleep_exit"
CONF_ON_SCAN_START = "on_scan_start"
CONF_ON_SCAN_END = "on_scan_end"
CONF_ON_SCAN_WAITING = "on_scan_waiting"
CONF_ON_ENROLLMENT_WAITING = "on_enrollment_waiting"
CONF_ON_ENROLLMENT_FINISHED = "on_enrollment_finished"
CONF_ON_ENROLLMENT_FAILED = "on_enrollment_failed"
CONF_ON_FINGER_MISSING = "on_finger_missing"
CONF_ON_FINGER_MISSPLACED = "on_finger_missplaced"
CONF_ON_FINGER_MATCHED = "on_finger_matched"
CONF_ON_FINGER_NOT_FOUND = "on_finger_not_found"

# ========================== NAMESPACE ========================== #

fingerprint_grow_ns = cg.esphome_ns.namespace("fingerprint_grow")
FingerprintGrowComponent = fingerprint_grow_ns.class_(
    "FingerprintGrowComponent", cg.PollingComponent, uart.UARTDevice
)

# ========================== TRIGGER ========================== #

SleepEnterTrigger = fingerprint_grow_ns.class_(
    "SleepEnterTrigger", automation.Trigger.template()
)

SleepExitTrigger = fingerprint_grow_ns.class_(
    "SleepExitTrigger", automation.Trigger.template()
)

ScanStartTrigger = fingerprint_grow_ns.class_(
    "ScanStartTrigger", automation.Trigger.template()
)

ScanEndTrigger = fingerprint_grow_ns.class_(
    "ScanEndTrigger", automation.Trigger.template()
)

ScanWaitingTrigger = fingerprint_grow_ns.class_(
    "ScanWaitingTrigger", automation.Trigger.template()
)

EnrollmentWaitingTrigger = fingerprint_grow_ns.class_(
    "EnrollmentWaitingTrigger", automation.Trigger.template()
)

EnrollmentFinishedTrigger = fingerprint_grow_ns.class_(
    "EnrollmentFinishedTrigger", automation.Trigger.template()
)

EnrollmentFailedTrigger = fingerprint_grow_ns.class_(
    "EnrollmentFailedTrigger", automation.Trigger.template()
)

FingerMissingTrigger = fingerprint_grow_ns.class_(
    "FingerMissingTrigger", automation.Trigger.template()
)

FingerMissplaceTrigger = fingerprint_grow_ns.class_(
    "FingerMissplacedTrigger", automation.Trigger.template()
)

FingerMatchedTrigger = fingerprint_grow_ns.class_(
    "FingerMatchedTrigger", automation.Trigger.template()
)

FingerNotFoundTrigger = fingerprint_grow_ns.class_(
    "FingerNotFoundTrigger", automation.Trigger.template()
)

# ========================== ACTIONS DECLARATION ========================== #

StartEnrollmentAction = fingerprint_grow_ns.class_("StartEnrollmentAction", automation.Action)
CancelEnrollmentAction = fingerprint_grow_ns.class_("CancelEnrollmentAction", automation.Action)
DeleteTemplateAction = fingerprint_grow_ns.class_("DeleteTemplateAction", automation.Action)
DeleteAllTemplatesAction = fingerprint_grow_ns.class_("DeleteAllTemplatesAction", automation.Action)
AuraLedControlAction = fingerprint_grow_ns.class_("AuraLedControlAction", automation.Action)

# ========================== ENUMS ========================== #

AuraLEDState = fingerprint_grow_ns.enum("GrowAuraLEDState", True)
AURA_LED_STATES = {
    "BREATHING": AuraLEDState.BREATHING,
    "FLASHING": AuraLEDState.FLASHING,
    "ALWAYS_ON": AuraLEDState.ALWAYS_ON,
    "ALWAYS_OFF": AuraLEDState.ALWAYS_OFF,
    "GRADUAL_ON": AuraLEDState.GRADUAL_ON,
    "GRADUAL_OFF": AuraLEDState.GRADUAL_OFF,
}
validate_aura_led_states = cv.enum(AURA_LED_STATES, upper=True)

AuraLEDColor = fingerprint_grow_ns.enum("GrowAuraLEDColor", True)
AURA_LED_COLORS = {
    "RED": AuraLEDColor.RED,
    "BLUE": AuraLEDColor.BLUE,
    "PURPLE": AuraLEDColor.PURPLE,
    "GREEN": AuraLEDColor.GREEN,
    "YELLOW": AuraLEDColor.YELLOW,
    "CYAN": AuraLEDColor.CYAN,
    "WHITE": AuraLEDColor.WHITE,
}
validate_aura_led_colors = cv.enum(AURA_LED_COLORS, upper=True)

# ========================== VALIDATION ========================== #

def validate(config):
    if CONF_SENSOR_POWER_PIN in config and CONF_SENSING_PIN not in config:
        raise cv.Invalid("You cannot use the Sensor Power Pin without a Sensing Pin")
    if CONF_IDLE_PERIOD_TO_SLEEP in config and CONF_SENSOR_POWER_PIN not in config:
        raise cv.Invalid(
            "You cannot have an Idle Period to Sleep without a Sensor Power Pin"
        )
    return config

# ========================== CONFIG SCHEMA ========================== #

CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(FingerprintGrowComponent),
            cv.Optional(CONF_SENSING_PIN): pins.gpio_input_pin_schema,
            cv.Optional(CONF_SENSOR_POWER_PIN): pins.gpio_output_pin_schema,
            cv.Optional(
                CONF_IDLE_PERIOD_TO_SLEEP
            ): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_PASSWORD): cv.uint32_t,
            cv.Optional(CONF_NEW_PASSWORD): cv.uint32_t,
            cv.Optional(CONF_ON_SLEEP_ENTER): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(
                        SleepEnterTrigger
                    ),
                }
            ),
            cv.Optional(CONF_ON_SLEEP_EXIT): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(
                        SleepExitTrigger
                    ),
                }
            ),
            cv.Optional(CONF_ON_SCAN_START): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(
                        ScanStartTrigger
                    ),
                }
            ),
            cv.Optional(CONF_ON_SCAN_END): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(
                        ScanEndTrigger
                    ),
                }
            ),
            cv.Optional(CONF_ON_SCAN_WAITING): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(
                        ScanWaitingTrigger
                    ),
                }
            ),
            cv.Optional(CONF_ON_ENROLLMENT_WAITING): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(
                        EnrollmentWaitingTrigger
                    ),
                }
            ),
            cv.Optional(CONF_ON_ENROLLMENT_FINISHED): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(
                        EnrollmentFinishedTrigger
                    ),
                }
            ),
            cv.Optional(CONF_ON_ENROLLMENT_FAILED): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(
                        EnrollmentFailedTrigger
                    ),
                }
            ),
        }
    )
    .extend(cv.polling_component_schema("500ms"))
    .extend(uart.UART_DEVICE_SCHEMA),
    validate,
)

FINGERPRINT_GROW_LED_CONTROL_ACTION_SCHEMA = cv.maybe_simple_value(
    {
        cv.GenerateID(): cv.use_id(FingerprintGrowComponent),
        cv.Required(CONF_STATE): cv.templatable(cv.boolean),
    },
    key=CONF_STATE,
)

# ========================== CODE GEN ========================== #

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    if CONF_PASSWORD in config:
        password = config[CONF_PASSWORD]
        cg.add(var.set_password(password))
    await uart.register_uart_device(var, config)

    if CONF_NEW_PASSWORD in config:
        new_password = config[CONF_NEW_PASSWORD]
        cg.add(var.set_new_password(new_password))

    if CONF_SENSING_PIN in config:
        sensing_pin = await cg.gpio_pin_expression(config[CONF_SENSING_PIN])
        cg.add(var.set_sensing_pin(sensing_pin))

    if CONF_SENSOR_POWER_PIN in config:
        sensor_power_pin = await cg.gpio_pin_expression(config[CONF_SENSOR_POWER_PIN])
        cg.add(var.set_sensor_power_pin(sensor_power_pin))

    if CONF_IDLE_PERIOD_TO_SLEEP in config:
        idle_period_to_sleep_ms = config[CONF_IDLE_PERIOD_TO_SLEEP]
        cg.add(var.set_idle_period_to_sleep_ms(idle_period_to_sleep_ms))

    for conf in config.get(CONF_ON_SLEEP_ENTER, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [], conf)

    for conf in config.get(CONF_ON_SLEEP_EXIT, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [], conf)

    for conf in config.get(CONF_ON_SCAN_START, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [], conf)

    for conf in config.get(CONF_ON_SCAN_END, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [], conf)

    for conf in config.get(CONF_ON_SCAN_WAITING, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [], conf)

    for conf in config.get(CONF_ON_ENROLLMENT_WAITING, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(
            trigger, [(cg.uint8, "scan_num"), (cg.uint16, "finger_id")], conf
        )

    for conf in config.get(CONF_ON_ENROLLMENT_FINISHED, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [(cg.uint16, "finger_id")], conf)

    for conf in config.get(CONF_ON_ENROLLMENT_FAILED, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [(cg.uint16, "finger_id")], conf)

    for conf in config.get(CONF_ON_FINGER_MATCHED, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(
            trigger, [(cg.uint16, "finger_id"), (cg.uint16, "confidence")], conf
        )

    for conf in config.get(CONF_ON_FINGER_NOT_FOUND, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [], conf)

    for conf in config.get(CONF_ON_FINGER_MISSPLACED, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [], conf)

    for conf in config.get(CONF_ON_FINGER_MISSING, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [], conf)

# ========================== ACTIONS REGISTRACTION ========================== #

@automation.register_action(
    "fingerprint_grow.start_enroll",
    StartEnrollmentAction,
    cv.maybe_simple_value(
        {
            cv.GenerateID(): cv.use_id(FingerprintGrowComponent),
            cv.Required(CONF_FINGER_ID): cv.templatable(cv.uint16_t),
            cv.Optional(CONF_NUM_SCANS): cv.templatable(cv.uint8_t),
        },
        key=CONF_FINGER_ID,
    ),
)
async def fingerprint_grow_enroll_to_code(config, action_id, template_arg, args):
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])

    template_ = await cg.templatable(config[CONF_FINGER_ID], args, cg.uint16)
    cg.add(var.set_finger_id(template_))
    if CONF_NUM_SCANS in config:
        template_ = await cg.templatable(config[CONF_NUM_SCANS], args, cg.uint8)
        cg.add(var.set_num_scans(template_))
    return var


@automation.register_action(
    "fingerprint_grow.cancel_enroll",
    CancelEnrollmentAction,
    cv.Schema(
        {
            cv.GenerateID(): cv.use_id(FingerprintGrowComponent),
        }
    ),
)
async def fingerprint_grow_cancel_enroll_to_code(config, action_id, template_arg, args):
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])
    return var


@automation.register_action(
    "fingerprint_grow.delete_template",
    DeleteTemplateAction,
    cv.maybe_simple_value(
        {
            cv.GenerateID(): cv.use_id(FingerprintGrowComponent),
            cv.Required(CONF_FINGER_ID): cv.templatable(cv.uint16_t),
        },
        key=CONF_FINGER_ID,
    ),
)
async def fingerprint_grow_delete_to_code(config, action_id, template_arg, args):
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])

    template_ = await cg.templatable(config[CONF_FINGER_ID], args, cg.uint16)
    cg.add(var.set_finger_id(template_))
    return var


@automation.register_action(
    "fingerprint_grow.delete_all_templates",
    DeleteAllTemplatesAction,
    cv.Schema(
        {
            cv.GenerateID(): cv.use_id(FingerprintGrowComponent),
        }
    ),
)
async def fingerprint_grow_delete_all_to_code(config, action_id, template_arg, args):
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])
    return var

@automation.register_action(
    "fingerprint_grow.aura_led_control",
    AuraLedControlAction,
    cv.Schema(
        {
            cv.GenerateID(): cv.use_id(FingerprintGrowComponent),
            cv.Required(CONF_STATE): cv.templatable(validate_aura_led_states),
            cv.Required(CONF_SPEED): cv.templatable(cv.uint8_t),
            cv.Required(CONF_COLOR): cv.templatable(validate_aura_led_colors),
            cv.Required(CONF_COUNT): cv.templatable(cv.uint8_t),
        }
    ),
)
async def fingerprint_grow_aura_led_control_to_code(config, action_id, template_arg, args):
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])

    for key in [CONF_STATE, CONF_SPEED, CONF_COLOR, CONF_COUNT]:
        template_ = await cg.templatable(config[key], args, cg.uint8)
        cg.add(getattr(var, f"set_{key}")(template_))
    return var
