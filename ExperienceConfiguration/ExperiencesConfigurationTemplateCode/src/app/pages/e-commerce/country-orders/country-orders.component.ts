import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { NbMediaBreakpoint, NbMediaBreakpointsService, NbThemeService } from '@nebular/theme';
import { takeWhile } from 'rxjs/operators';

@Component({
  selector: 'ngx-country-orders',
  styleUrls: ['./country-orders.component.scss'],
  template: `
    <nb-card [size]="breakpoint.width >= breakpoints.md ? 'medium' : 'giant'" style="max-height: 340px;" [ngClass]="{'no-styling': !applyStyling}"  >
      <nb-card-header [ngStyle]="getTitleStyle()">{{caption}}</nb-card-header>
      <nb-card-body  [ngClass]="{'no-styling': !applyStyling}" >
        <ngx-country-orders-chart [ngStyle]="getCardBodyStyle()"
                                  [countryName]="categories"
                                  [data]="data"
                                  [labels]="categories"
                                  maxValue="20"
                                  [horizontal]="horizontal">
        </ngx-country-orders-chart>
      </nb-card-body>
    </nb-card>
  `,
})
export class CountryOrdersComponent implements OnInit, OnDestroy {

  private alive = true;

  @Input() inputData: {[key: string]: number} = {};
  @Input() title: string;
  @Input() caption: string;
  @Input() horizontal: boolean;
  @Input() applyStyling: string;

  categories: string[] = [];
  data: number[] = [];
  breakpoint: NbMediaBreakpoint = { name: '', width: 0 };
  breakpoints: any;

  constructor(private themeService: NbThemeService,
              private breakpointService: NbMediaBreakpointsService) {
    this.breakpoints = this.breakpointService.getBreakpointsMap();
  }

  ngOnInit() {
    this.processInputData();
    this.themeService.onMediaQueryChange()
      .pipe(takeWhile(() => this.alive))
      .subscribe(([oldValue, newValue]) => {
        this.breakpoint = newValue;
      });
  }

  processInputData() {
    this.categories = Object.keys(this.inputData);
    this.data = Object.values(this.inputData);
  }

  ngOnChanges() {
    this.processInputData(); // Re-process when input changes
  }

  getTitleStyle() {
    return this.applyStyling ? {
      'display': 'none'
    } : {};
  }

  getCardBodyStyle() {
    return this.applyStyling ? {
      'transform': 'scale(0.76) translateY(-48px)'
    } : {};
  }

  ngOnDestroy() {
    this.alive = false;
  }
}
