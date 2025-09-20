#include "fingerprint_grow.h"
#include "esphome/core/log.h"
#include <cinttypes>

namespace esphome {
namespace fingerprint_grow {

static const char *const TAG = "fingerprint_grow";

// Based on Adafruit's library: https://github.com/adafruit/Adafruit-Fingerprint-Sensor-Library

void FingerprintGrowComponent::update() {
  if (this->enrollment_image_ > this->enrollment_buffers_) {
    this->finish_enrollment(this->save_fingerprint_());
    return;
  }

  if (this->has_sensing_pin_) {
    // A finger touch results in a low level (digital_read() == false)
    if (this->sensing_pin_->digital_read()) {
      ESP_LOGV(TAG, "No touch sensing");
      this->waiting_removal_ = false;
      if ((this->enrollment_image_ == 0) &&  // Not in enrolment process
          (millis() - this->last_transfer_ms_ > this->idle_period_to_sleep_ms_) && (this->is_sensor_awake_)) {
        this->sensor_sleep_();
      }
      return;
    } else if (!this->waiting_removal_) {
      this->finger_scan_start_callback_.call();
    }
  }

  if (this->waiting_removal_) {
    if ((!this->has_sensing_pin_) && (this->scan_image_(1) == NO_FINGER)) {
      ESP_LOGD(TAG, "Finger removed");
      this->waiting_removal_ = false;
    }
    return;
  }


  if (this->enrollment_image_ == 0) {
    this->scan_and_match_();
    return;
  }

  uint8_t result = this->scan_image_(this->enrollment_image_);
  if (result == NO_FINGER) {
    return;
  }
  this->waiting_removal_ = true;
  if (result != OK) {
    this->finish_enrollment(result);
    return;
  }
  this->enrollment_scan_callback_.call(this->enrollment_image_, this->enrollment_slot_);
  ++this->enrollment_image_;
}

void FingerprintGrowComponent::setup() {
  this->has_sensing_pin_ = (this->sensing_pin_ != nullptr);
  this->has_power_pin_ = (this->sensor_power_pin_ != nullptr);

  // Call pins setup, so we effectively apply the config generated from the yaml file.
  if (this->has_sensing_pin_) {
    this->sensing_pin_->setup();
  }
  if (this->has_power_pin_) {
    // Starts with output low (disabling power) to avoid glitches in the sensor
    this->sensor_power_pin_->digital_write(false);
    this->sensor_power_pin_->setup();

    // If the user didn't specify an idle period to sleep, applies the default.
    if (this->idle_period_to_sleep_ms_ == UINT32_MAX) {
      this->idle_period_to_sleep_ms_ = DEFAULT_IDLE_PERIOD_TO_SLEEP_MS;
    }
  }
  


}

void FingerprintGrowComponent::enroll_fingerprint(uint16_t finger_id, uint8_t num_buffers) {
  
}

void FingerprintGrowComponent::finish_enrollment(uint8_t result) {
  
}

bool FingerprintGrowComponent::set_password_() {
  ESP_LOGI(TAG, "Setting new password: %" PRIu32, this->new_password_);
  this->data_ = {SET_PASSWORD, (uint8_t) (this->new_password_ >> 24), (uint8_t) (this->new_password_ >> 16),
                 (uint8_t) (this->new_password_ >> 8), (uint8_t) (this->new_password_ & 0xFF)};
  if (this->send_command_() == OK) {
    ESP_LOGI(TAG, "New password successfully set");
    ESP_LOGI(TAG, "Define the new password in your configuration and reflash now");
    ESP_LOGW(TAG, "!!!Forgetting the password will render your device unusable!!!");
    return true;
  }
  return false;
}

bool FingerprintGrowComponent::get_parameters_() {
  ESP_LOGD(TAG, "Getting parameters");
  this->data_ = {READ_SYS_PARAM};
  if (this->send_command_() == OK) {
    ESP_LOGD(TAG, "Got parameters");        // Bear in mind data_[0] is the transfer status,
    if (this->status_sensor_ != nullptr) {  // the parameters table start at data_[1]
      this->status_sensor_->publish_state(((uint16_t) this->data_[1] << 8) | this->data_[2]);
    }
    this->system_identifier_code_ = ((uint16_t) this->data_[3] << 8) | this->data_[4];
    this->capacity_ = ((uint16_t) this->data_[5] << 8) | this->data_[6];
    if (this->capacity_sensor_ != nullptr) {
      this->capacity_sensor_->publish_state(this->capacity_);
    }
    if (this->security_level_sensor_ != nullptr) {
      this->security_level_sensor_->publish_state(((uint16_t) this->data_[7] << 8) | this->data_[8]);
    }
    if (this->enrolling_binary_sensor_ != nullptr) {
      this->enrolling_binary_sensor_->publish_state(false);
    }
    this->get_fingerprint_count_();
    return true;
  }
  return false;
}

void FingerprintGrowComponent::get_fingerprint_count_() {
  ESP_LOGD(TAG, "Getting fingerprint count");
  this->data_ = {TEMPLATE_COUNT};
  if (this->send_command_() == OK) {
    ESP_LOGD(TAG, "Got fingerprint count");
    if (this->fingerprint_count_sensor_ != nullptr)
      this->fingerprint_count_sensor_->publish_state(((uint16_t) this->data_[1] << 8) | this->data_[2]);
  }
}

void FingerprintGrowComponent::delete_fingerprint(uint16_t finger_id) {
  
}

void FingerprintGrowComponent::delete_all_fingerprints() {
  
}

void FingerprintGrowComponent::aura_led_control(uint8_t state, uint8_t speed, uint8_t color, uint8_t count) {

}


void FingerprintGrowComponent::sensor_wakeup_() {
  // Immediately return if there is no power pin or the sensor is already on
  if ((!this->has_power_pin_) || (this->is_sensor_awake_))
    return;

  this->sensor_power_pin_->digital_write(true);
  this->is_sensor_awake_ = true;

  uint8_t byte = TIMEOUT;

  // Wait for the byte HANDSHAKE_SIGN from the sensor meaning it is operational.
  for (uint16_t timer = 0; timer < WAIT_FOR_WAKE_UP_MS; timer++) {
    if (this->available() > 0) {
      byte = this->read();

      /* If the received byte is zero, the UART probably misinterpreted a raising edge on
       * the RX pin due the power up as byte "zero" - I verified this behaviour using
       * the esp32-arduino lib. So here we just ignore this fake byte.
       */
      if (byte != 0)
        break;
    }
    delay(1);
  }

  /* Lets check if the received by is a HANDSHAKE_SIGN, otherwise log an error
   * message and try to continue on the best effort.
   */
  if (byte == HANDSHAKE_SIGN) {
    ESP_LOGD(TAG, "Sensor has woken up!");
  } else if (byte == TIMEOUT) {
    ESP_LOGE(TAG, "Timed out waiting for sensor wake-up");
  } else {
    ESP_LOGE(TAG, "Received wrong byte from the sensor during wake-up: 0x%.2X", byte);
  }

  /* Next step, we must authenticate with the password. We cannot call check_password_ here
   * neither use data_ to store the command because it might be already in use by the caller
   * of send_command_()
   */
  std::vector<uint8_t> buffer = {VERIFY_PASSWORD, (uint8_t) (this->password_ >> 24), (uint8_t) (this->password_ >> 16),
                                 (uint8_t) (this->password_ >> 8), (uint8_t) (this->password_ & 0xFF)};

  if (this->transfer_(&buffer) != OK) {
    ESP_LOGE(TAG, "Wrong password");
  }
}

void FingerprintGrowComponent::sensor_sleep_() {
  // Immediately return if the power pin feature is not implemented
  if (!this->has_power_pin_)
    return;

  this->sensor_power_pin_->digital_write(false);
  this->is_sensor_awake_ = false;
  ESP_LOGD(TAG, "Fingerprint sensor is now in sleep mode.");
}

void FingerprintGrowComponent::dump_config() {
  ESP_LOGCONFIG(TAG,
                "GROW_FINGERPRINT_READER:\n"
                "  System Identifier Code: 0x%.4X\n"
                "  Touch Sensing Pin: %s\n"
                "  Sensor Power Pin: %s",
                this->system_identifier_code_,
                this->has_sensing_pin_ ? this->sensing_pin_->dump_summary().c_str() : "None",
                this->has_power_pin_ ? this->sensor_power_pin_->dump_summary().c_str() : "None");
  if (this->idle_period_to_sleep_ms_ < UINT32_MAX) {
    ESP_LOGCONFIG(TAG, "  Idle Period to Sleep: %" PRIu32 " ms", this->idle_period_to_sleep_ms_);
  } else {
    ESP_LOGCONFIG(TAG, "  Idle Period to Sleep: Never");
  }
  LOG_UPDATE_INTERVAL(this);
  if (this->fingerprint_count_sensor_) {
    LOG_SENSOR("  ", "Fingerprint Count", this->fingerprint_count_sensor_);
    ESP_LOGCONFIG(TAG, "    Current Value: %u", (uint16_t) this->fingerprint_count_sensor_->get_state());
  }
  if (this->status_sensor_) {
    LOG_SENSOR("  ", "Status", this->status_sensor_);
    ESP_LOGCONFIG(TAG, "    Current Value: %u", (uint8_t) this->status_sensor_->get_state());
  }
  if (this->capacity_sensor_) {
    LOG_SENSOR("  ", "Capacity", this->capacity_sensor_);
    ESP_LOGCONFIG(TAG, "    Current Value: %u", (uint16_t) this->capacity_sensor_->get_state());
  }
  if (this->security_level_sensor_) {
    LOG_SENSOR("  ", "Security Level", this->security_level_sensor_);
    ESP_LOGCONFIG(TAG, "    Current Value: %u", (uint8_t) this->security_level_sensor_->get_state());
  }
  if (this->last_finger_id_sensor_) {
    LOG_SENSOR("  ", "Last Finger ID", this->last_finger_id_sensor_);
    ESP_LOGCONFIG(TAG, "    Current Value: %" PRIu32, (uint32_t) this->last_finger_id_sensor_->get_state());
  }
  if (this->last_confidence_sensor_) {
    LOG_SENSOR("  ", "Last Confidence", this->last_confidence_sensor_);
    ESP_LOGCONFIG(TAG, "    Current Value: %" PRIu32, (uint32_t) this->last_confidence_sensor_->get_state());
  }
}

}  // namespace fingerprint_grow
}  // namespace esphome
