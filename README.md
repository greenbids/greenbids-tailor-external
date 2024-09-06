
# 🪡 Greenbids Tailor

Bring **traffic shaping** to your own cloud!

[![Greenbids logo](https://www.greenbids.ai/wp-content/uploads/2023/11/greenbids-logo.svg)](https://www.greenbids.ai)

[![GNU AGPL v3 License](https://img.shields.io/badge/license-GNU%20AGPL%20v3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

## 🤖 API Reference

### Interactions

Following the interaction diagram provided by the [OpenRTB API Specification (version 2.5) (§2)](https://www.iab.com/wp-content/uploads/2016/03/OpenRTB-API-Specification-Version-2-5-FINAL.pdf) here is an example of where the Greenbids Tailor product must be called.

```mermaid
sequenceDiagram
    participant Publisher
    activate Publisher

    box rgba(128, 128, 128, 0.33) Partner Network
        participant SSP as RTB Exchange
        participant GB as Greenbids Tailor
    end

    Publisher ->>+ SSP: 0. Ad Request

    rect rgba(30, 183, 136, 0.66)
    SSP ->>+ GB: PUT / @[Fabric, ...]
    GB -->>- SSP: 200 @[Fabric, ...]
    end

    loop for each request where fabric.prediction.shouldSend
        SSP ->>+ Bidder : 1. Bid Request
        alt 200
        Bidder -->> SSP: Bid Response
        else 204
        Bidder -->>- SSP: No Response
        end
    end

    opt fabric.prediction.<br>isExploration
        rect rgba(30, 183, 136, 0.66)
            SSP -)+ GB: POST / @[Fabric, ...]
            GB -->>- SSP: 200
        end
    end
    GB --) greenbids.ai: telemetry

    note over Publisher,SSP: Continue auction process
    deactivate SSP
    deactivate Publisher
```

### Routes

See API documentation [online](https://greenbids.github.io/greenbids-tailor-external/).

## 🚀 Deployment

Depending on your current stack, find the best way to deploy this service.

* Executable

  ```bash
  pip install ./python
  uvicorn greenbids.tailor:app
  ```

* Docker

  ```bash
  docker run -P ghcr.io/greenbids/tailor:latest
  ```

* Helm

  ```bash
  helm install --create-namespace --namespace greenbids tailor oci://ghcr.io/greenbids/charts/tailor
  ```
