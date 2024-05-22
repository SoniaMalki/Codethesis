import { Component, OnDestroy, Input } from '@angular/core';
import { ProgressInfo, StatsProgressBarData } from '../../../@core/data/stats-progress-bar';
import { takeWhile } from 'rxjs/operators';

@Component({
  selector: 'ngx-progress-section',
  styleUrls: ['./progress-section.component.scss'],
  templateUrl: './progress-section.component.html',
})
export class ECommerceProgressSectionComponent implements OnDestroy {

  private alive = true;
  @Input() progressInfoData: any[];


  constructor(private statsProgressBarService: StatsProgressBarData) {
   
  }

  ngOnDestroy() {
    this.alive = true;
  }
}
