import { Component } from '@angular/core';
import {
  NgxPopoverCardComponent, NgxPopoverFormComponent,
  NgxPopoverTabsComponent,
} from './popover-examples.component';

@Component({
  selector: 'ngx-popovers',
  styleUrls: ['./popovers.component.scss'],
  templateUrl: './popovers.component.html',
})
export class PopoversComponent {
  tabsComponent = NgxPopoverTabsComponent;
  cardComponent = NgxPopoverCardComponent;
  formComponent = NgxPopoverFormComponent;
  example = JSON.stringify({
    "id": 54,
    "taskset": {
        "id": 104,
        "action": "generate",
        "parameters": {
            "id": 54,
            "numberOfCores": 4,
            "listOfMaxUtilization": [],
            "listOfTasksPerTaskset": null,
            "tasksetCount": 3,
            "listOfInterferenceFactors": [],
            "listOfProbabilityFactors": [],
            "minPeriod": 50,
            "maxPeriod": 1000,
            "listOfPeriodGenerationMethods": [],
            "granularity": []
        },
        "tasksetId": null
    },
    "assignment": {
        "id": 54,
        "action": "generate",
        "parameters": {
            "id": 4,
            "assignmentMethod": "",
            "cittaCriteria": []
        },
        "tasksetId": null,
        "assignmentId": null
    },
    "scheduling": {
        "id": 54,
        "action": "generate",
        "parameters": {
            "id": 4,
            "schedulingAlgorithms": []
        },
        "tasksetId": null,
        "assignmentId": null,
        "schedulingId": null
    }
})
}
