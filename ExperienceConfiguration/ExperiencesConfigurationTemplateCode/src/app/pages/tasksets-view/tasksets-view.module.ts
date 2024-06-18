import { NgModule } from '@angular/core';
import {
  NbActionsModule,
  NbButtonModule,
  NbCardModule,
  NbTabsetModule,
  NbUserModule,
  NbRadioModule,
  NbSelectModule,
  NbInputModule,
  NbListModule,
  NbIconModule,
  NbDialogModule,
} from '@nebular/theme';
import { NgxEchartsModule } from 'ngx-echarts';

import { ThemeModule } from '../../@theme/theme.module';
import { DataSamplesViewComponent } from './data-samples-view.component';
import { StatusCardComponent } from './status-card/status-card.component';
import { ContactsComponent } from './contacts/contacts.component';
import { RoomsComponent } from './rooms/rooms.component';
import { RoomSelectorComponent } from './rooms/room-selector/room-selector.component';
import { TemperatureComponent } from './temperature/temperature.component';
import { TemperatureDraggerComponent } from './temperature/temperature-dragger/temperature-dragger.component';
import { KittenComponent } from './kitten/kitten.component';
import { SecurityCamerasComponent } from './security-cameras/security-cameras.component';
import { ElectricityComponent } from './electricity/electricity.component';
import { ElectricityChartComponent } from './electricity/electricity-chart/electricity-chart.component';
import { SolarComponent } from './solar/solar.component';
import { PlayerComponent } from './rooms/player/player.component';
import { TrafficChartComponent } from './traffic/traffic-chart.component';
import { FormsModule as ngFormsModule } from '@angular/forms';
import { SmartTableComponent } from '../tables/smart-table/smart-table.component'
import { TablesModule } from '../tables/tables.module'
import { FormsModule } from '../forms/forms.module';
import { DataSampleEditIconComponent } from './data-sample-edit-icon/data-sample-edit-icon-component';
import { DataSampleDeleteIconComponent } from './data-sample-delete-icon/data-sample-delete-icon.component';
import { DeleteConfirmModalComponent } from './delete-confirm-modal/delete-confirm-modal.component';
import { DataSampleEditFormComponent } from './data-sample-edit-form/data-sample-edit-form.component';
import { DataSampleCreateFormComponent } from './data-sample-create-form/data-sample-create-form.component'


@NgModule({
  imports: [
    ngFormsModule,
    ThemeModule,
    NbCardModule,
    NbUserModule,
    NbButtonModule,
    NbTabsetModule,
    NbActionsModule,
    NbRadioModule,
    NbSelectModule,
    NbListModule,
    NbIconModule,
    NbButtonModule,
    NbInputModule,
    NgxEchartsModule,
    TablesModule,
    FormsModule,
    NbDialogModule
  ],
  declarations: [
    DataSamplesViewComponent,
    StatusCardComponent,
    TemperatureDraggerComponent,
    ContactsComponent,
    RoomSelectorComponent,
    TemperatureComponent,
    RoomsComponent,
    KittenComponent,
    SecurityCamerasComponent,
    ElectricityComponent,
    ElectricityChartComponent,
    PlayerComponent,
    SolarComponent,
    TrafficChartComponent,
    DataSampleEditIconComponent,
    DataSampleDeleteIconComponent,
    DeleteConfirmModalComponent,
    DataSampleEditFormComponent,
    DataSampleCreateFormComponent,
  ],
})
export class DataSampleViewModule { }
