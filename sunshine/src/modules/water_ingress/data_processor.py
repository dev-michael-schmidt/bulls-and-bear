
"""
- Never create:
def __init__(self)

- never create a global
use `from common import Config as cfg` instead

- You can use `@staticmethod` on every method
"""
import copy
import statistics


class DataProcessor:

    """

    """

    @staticmethod
    def process_pre_result(pre_data):
        """
        Fast Fail on duplicate PKs to maintain consistency.
        Convert raw pre_result data into a structured dictionary.
        """
        pre_dict = {}

        for row in pre_data["pre_obs_result"]:
            pk = row["PK"]
            if pk not in pre_dict:
                pre_dict[pk] = {
                    "pre_CloseATGRecordID": row["CloseATGRecordID"],
                    "pre_CloseATGRecordDateTime": row["CloseATGRecordDateTime"],
                    "pre_CloseWaterLevelCurrent": row["CloseWaterLevelCurrent"],
                    "pre_CloseProductLevelCurrent": row["CloseProductLevelCurrent"],
                    "pre_CloseProductVolumeCurrent": row["CloseProductVolumeCurrent"],
                    "pre_CloseProductTemperatureCurrent": row["CloseProductTemperatureCurrent"],
                }
            else:
                raise ValueError(f"Multiple records found for PK {pk}.")

        return pre_dict

    # pylint: disable=too-many-locals
    @staticmethod
    def build_obs_result(atg_result, pre_dict, last_hour_start):
        """ Builds the final observation result with min/max values and computed deltas. """
        min_obs_values, max_obs_values = {}, {}
        water_levels, product_levels, product_volumes, product_temperatures = {}, {}, {}, {}
        key_set = set()

        for row in atg_result:
            key = f"{row['companyID']}-{row['siteID']}-{row['TankID']}"
            key_set.add(key)

            # Initialize min values using previous hour close if available
            if key not in min_obs_values:
                min_obs_values[key] = copy.deepcopy(row)
                if key in pre_dict:
                    pre_values = pre_dict[key]
                    min_obs_values[key].update({
                        'ATGRecordID': pre_values['pre_CloseATGRecordID'],
                        'ATGRecordDateTime': pre_values['pre_CloseATGRecordDateTime'],
                        'WaterLevelCurrent': pre_values['pre_CloseWaterLevelCurrent'],
                        'ProductLevelCurrent': pre_values['pre_CloseProductLevelCurrent'],
                        'ProductVolumeCurrent': pre_values['pre_CloseProductVolumeCurrent'],
                        'ProductTemperatureCurrent': pre_values['pre_CloseProductTemperatureCurrent']
                    })

                    # Store initial values for median calculations
                    water_levels[key] = [pre_values['pre_CloseWaterLevelCurrent']]
                    product_levels[key] = [pre_values['pre_CloseProductLevelCurrent']]
                    product_volumes[key] = [pre_values['pre_CloseProductVolumeCurrent']]
                    product_temperatures[key] = [pre_values['pre_CloseProductTemperatureCurrent']]
            else:
                if min_obs_values[key]['ATGRecordDateTime'] > row['ATGRecordDateTime']:
                    min_obs_values[key] = row  # Replace with the earlier record

            # Track max values
            if key not in max_obs_values or max_obs_values[key]['ATGRecordDateTime'] < row['ATGRecordDateTime']:
                max_obs_values[key] = row

            # Collect values for median calculation
            water_levels.setdefault(key, []).append(row['WaterLevelCurrent'])
            product_levels.setdefault(key, []).append(row['ProductLevelCurrent'])
            product_volumes.setdefault(key, []).append(row['ProductVolumeCurrent'])
            product_temperatures.setdefault(key, []).append(row['ProductTemperatureCurrent'])

        # Build the final result list
        result = []
        for key in key_set:
            min_val, max_val = min_obs_values[key], max_obs_values[key]

            result.append({
                'companyID': min_val['companyID'],
                'siteID': min_val['siteID'],
                'TankID': min_val['TankID'],
                'GradeID': min_val.get('GradeID', None),
                'ATGRecordDateHour': last_hour_start,

                'OpenATGRecordID': min_val['ATGRecordID'],
                'CloseATGRecordID': max_val['ATGRecordID'],

                'OpenATGRecordDateTime': min_val['ATGRecordDateTime'],
                'CloseATGRecordDateTime': max_val['ATGRecordDateTime'],

                'OpenWaterLevelCurrent': min_val['WaterLevelCurrent'],
                'CloseWaterLevelCurrent': max_val['WaterLevelCurrent'],

                'OpenProductLevelCurrent': min_val['ProductLevelCurrent'],
                'CloseProductLevelCurrent': max_val['ProductLevelCurrent'],

                'OpenProductVolumeCurrent': min_val['ProductVolumeCurrent'],
                'CloseProductVolumeCurrent': max_val['ProductVolumeCurrent'],

                'OpenProductTemperatureCurrent': min_val['ProductTemperatureCurrent'],
                'CloseProductTemperatureCurrent': max_val['ProductTemperatureCurrent'],

                'periodWaterLevelDelta': max_val['WaterLevelCurrent'] - min_val['WaterLevelCurrent'],
                'periodProductLevelDelta': max_val['ProductLevelCurrent'] - min_val['ProductLevelCurrent'],
                'periodProductVolumeDelta': max_val['ProductVolumeCurrent'] - min_val['ProductVolumeCurrent'],

                'WaterLevelMedian': statistics.median(water_levels[key]),
                'ProductLevelMedian': statistics.median(product_levels[key]),
                'ProductVolumeMedian': statistics.median(product_volumes[key]),
                'ProductTemperatureMedian': statistics.median(product_temperatures[key])
            })

        return result
