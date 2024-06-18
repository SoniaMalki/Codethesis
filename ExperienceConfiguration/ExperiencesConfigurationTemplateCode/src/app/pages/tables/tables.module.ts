import { NgModule } from '@angular/core';
import { NbCardModule, NbIconModule, NbInputModule, NbButtonModule, NbTreeGridModule } from '@nebular/theme';
import { Ng2SmartTableModule } from 'ng2-smart-table';

import { ThemeModule } from '../../@theme/theme.module';
import { TablesRoutingModule, routedComponents } from './tables-routing.module';
import { FsIconComponent } from './tree-grid/tree-grid.component';
import { SmartTableComponent } from './smart-table/smart-table.component';
import { ClickableIconComponent } from './clickable-icon/clickable-icon.component';
import { CustomTextCellComponent } from './custom-text-cell/custom-text-cell.component';


@NgModule({
  imports: [
    NbCardModule,
    NbTreeGridModule,
    NbIconModule,
    NbInputModule,
    NbButtonModule,
    ThemeModule,
    TablesRoutingModule,
    Ng2SmartTableModule,
  ],
  declarations: [
    ...routedComponents,
    FsIconComponent,
    ClickableIconComponent,
    CustomTextCellComponent,
  ],
  exports: [
    SmartTableComponent,
    ClickableIconComponent,
    CustomTextCellComponent  
  ],
  bootstrap: [SmartTableComponent]
})
export class TablesModule { }
